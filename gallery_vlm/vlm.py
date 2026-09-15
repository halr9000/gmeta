from __future__ import annotations
import json, httpx

class VLMError(RuntimeError): pass

def caption_image(path: str, *, endpoint: str, model: str, prompt: str, timeout: float = 300.0) -> tuple[str, list[str]]:
    import base64, mimetypes
    data=base64.b64encode(open(path,'rb').read()).decode()
    mime=mimetypes.guess_type(path)[0] or 'image/jpeg'
    payload={"model":model,"temperature":0,"max_tokens":256,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":"Return JSON with caption (string) and tags (array of strings). Be visually grounded."},{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":f"data:{mime};base64,{data}"}}]}]}
    with httpx.Client(timeout=timeout) as client:
        r=client.post(endpoint.rstrip('/')+'/v1/chat/completions',json=payload)
        r.raise_for_status(); raw=r.json()["choices"][0]["message"].get("content","")
    if raw.startswith('```'):
        lines=raw.splitlines(); raw='\n'.join(lines[1:-1])
    try: obj=json.loads(raw)
    except json.JSONDecodeError as e: raise VLMError(f"invalid VLM JSON: {e}") from e
    caption=str(obj.get('caption') or '').strip()
    tags=obj.get('tags') or []
    if not caption: raise VLMError('VLM returned no caption')
    if not isinstance(tags,list): raise VLMError('VLM returned invalid tags')
    return caption, list(dict.fromkeys(str(x).strip() for x in tags if str(x).strip()))
