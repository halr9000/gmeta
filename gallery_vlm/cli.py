from __future__ import annotations
import json, logging, sys
from pathlib import Path
import typer
from rich.console import Console
from . import __version__
from .metadata import read_metadata, plan_metadata, write_metadata
from .vlm import DEFAULT_PROMPT, SYSTEM_PROMPT, caption_image
app=typer.Typer(help="Generate VLM captions and tags and write gallery-compatible XMP metadata.")
err=Console(stderr=True)

def version(v: bool):
    if v: print(f"gmeta {__version__}"); raise typer.Exit()
@app.callback(invoke_without_command=True)
def main(version_flag: bool=typer.Option(False,"--version","-V")):
    version(version_flag)

def files(paths:list[Path], recursive:bool):
    out=[]
    for p in paths:
        if p.is_file(): out.append(p)
        elif p.is_dir(): out += [x for x in (p.rglob('*') if recursive else p.iterdir()) if x.is_file() and x.suffix.lower() in {'.jpg','.jpeg','.png','.webp','.tif','.tiff'}]
    return list(dict.fromkeys(out))
@app.command()
def metadata(paths:list[Path]=typer.Argument(...,exists=True), recursive:bool=typer.Option(False,'--recursive','-r'), url:str=typer.Option('http://127.0.0.1:8166','--url','-u',help='OpenAI-compatible VLM server URL'), model:str=typer.Option('LFM2.5-VL-1.6B','--model'), prompt:str=typer.Option(DEFAULT_PROMPT,'--prompt'), dry_run:bool=typer.Option(False,'--dry-run','-n'), force:bool=typer.Option(False,'--force','-f',help='Process files that already have generated metadata'), replace_caption:bool=typer.Option(False,'--replace-caption',help='Replace an existing caption'), replace_tags:bool=typer.Option(False,'--replace-tags',help='Replace existing tags instead of merging'), backup:bool=typer.Option(False,'--backup'), json_output:bool=typer.Option(False,'--json'), quiet:bool=typer.Option(False,'--quiet')):
    """Caption images and merge tags into source metadata."""
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s',stream=sys.stderr)
    result=[]
    for path in files(paths,recursive):
        row={'path':str(path),'status':'failed'}
        try:
            meta=read_metadata(path); caption,tags=caption_image(str(path),endpoint=url,model=model,prompt=prompt)
            plan=plan_metadata(meta,caption,tags,skip_existing=not force,overwrite_caption=replace_caption,replace_tags=replace_tags)
            write_metadata(path,plan,dry_run=dry_run,backup=backup)
            row.update(status='unchanged' if not plan.changed else ('would-update' if dry_run else 'updated'),caption=plan.caption,tags=plan.tags)
            if not quiet and not json_output: err.print(f"{row['status']}: {path}")
        except Exception as exc:
            row['error']=str(exc); logging.error('%s: %s',path,exc)
        result.append(row)
    if json_output: print(json.dumps(result,ensure_ascii=False,indent=2))
    if any(x['status']=='failed' for x in result): raise typer.Exit(1)
if __name__=='__main__': app()