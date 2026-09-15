from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path

import httpx

SYSTEM_PROMPT = (
    "You caption images for a searchable media library. Be visually grounded and conservative. "
    'Return ONLY valid JSON matching exactly {"caption":"one precise sentence",'
    '"tags":["3-8 unique concise tags"]}. Tags must be unique, useful, and supported by visible content. '
    "Do not infer identities, sex/gender, ethnicity, age, brands, location, dates, or events."
)
DEFAULT_PROMPT = "Caption this image using the required JSON schema."


class VLMError(RuntimeError):
    """The VLM returned a response that gmeta cannot use."""


def caption_image(
    path: str,
    *,
    endpoint: str,
    model: str,
    prompt: str = DEFAULT_PROMPT,
    timeout: float = 300.0,
    system_prompt: str = SYSTEM_PROMPT,
) -> tuple[str, list[str]]:
    """Generate a caption and tags. ``prompt`` is added as the user message."""
    image_path = Path(path)
    data = base64.b64encode(image_path.read_bytes()).decode()
    mime = mimetypes.guess_type(str(image_path))[0] or "image/jpeg"
    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 256,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
                ],
            },
        ],
    }
    with httpx.Client(timeout=timeout) as client:
        response = client.post(endpoint.rstrip("/") + "/v1/chat/completions", json=payload)
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"].get("content", "")
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1])
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VLMError(f"invalid VLM JSON: {exc}") from exc
    caption = str(obj.get("caption") or "").strip()
    tags = obj.get("tags") or []
    if not caption:
        raise VLMError("VLM returned no caption")
    if not isinstance(tags, list):
        raise VLMError("VLM returned invalid tags")
    return caption, list(dict.fromkeys(str(tag).strip() for tag in tags if str(tag).strip()))
