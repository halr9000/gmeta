from __future__ import annotations
import json, logging, shutil, subprocess
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("gallery-vlm.metadata")
TAG_FIELDS = ("XMP-dc:Subject", "XMP-digiKam:TagsList", "XMP-lr:HierarchicalSubject")

@dataclass
class MetadataPlan:
    caption: str
    tags: list[str]
    changed: bool
    reason: str

def _values(value):
    if value is None: return []
    if isinstance(value, list): return [str(x) for x in value if str(x)]
    return [str(value)]

def read_metadata(path: Path) -> dict:
    proc = subprocess.run(["exiftool", "-j", "-G1", str(path)], check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)[0]

def plan_metadata(meta: dict, caption: str, tags: list[str], *, skip_existing: bool = True, overwrite_caption: bool = False, replace_tags: bool = False) -> MetadataPlan:
    old_caption = str(meta.get("XMP-dc:Description") or "").strip()
    old_tags=[]
    for field in TAG_FIELDS: old_tags.extend(_values(meta.get(field)))
    old_tags=list(dict.fromkeys(old_tags))
    if skip_existing and old_caption and old_tags:
        return MetadataPlan(caption=old_caption,tags=old_tags,changed=False,reason="existing caption and tags")
    new_caption=caption.strip() if overwrite_caption or not old_caption else old_caption
    incoming=list(dict.fromkeys(x.strip() for x in tags if x.strip()))
    new_tags=incoming if replace_tags else list(dict.fromkeys(old_tags+incoming))
    changed=(new_caption != old_caption) or (new_tags != old_tags)
    return MetadataPlan(new_caption,new_tags,changed,"update required" if changed else "unchanged")

def write_metadata(path: Path, plan: MetadataPlan, *, dry_run: bool = False, backup: bool = False) -> None:
    if not plan.changed: return
    if backup: shutil.copy2(path, str(path)+".gallery-vlm.bak")
    args=["exiftool", "-overwrite_original"]
    args += [f"-XMP-dc:Description={plan.caption}"]
    for field in TAG_FIELDS: args.append(f"-{field}=" + "|".join(plan.tags))
    args.append(str(path))
    if dry_run:
        log.info("dry-run write %s", path); return
    subprocess.run(args, check=True, capture_output=True, text=True)
    after=read_metadata(path)
    if str(after.get("XMP-dc:Description") or "").strip() != plan.caption: raise RuntimeError("post-write caption verification failed")
    for field in TAG_FIELDS:
        if _values(after.get(field)) != plan.tags: raise RuntimeError(f"post-write tag verification failed: {field}")
