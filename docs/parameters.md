# Parameter reference

Generated from the live CLI help. Regenerate with:

```bash
uv run python scripts/generate_docs.py
```

The `--prompt` value is added as the user message. The tested grounding and JSON rules remain in the system prompt.

## `gmeta metadata`

```text
                                                                                
 Usage: gmeta metadata [OPTIONS] {paths}...                                     
                                                                                
 Caption images and merge tags into source metadata.                            
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    paths      <path>  [required]                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --recursive        -r                                                        │
│ --url              -u      <str>  OpenAI-compatible VLM server URL           │
│                                   [default: http://127.0.0.1:8166]           │
│ --model                    <str>  [default: LFM2.5-VL-1.6B]                  │
│ --prompt                   <str>  [default: Caption this image using the     │
│                                   required JSON schema.]                     │
│ --dry-run          -n                                                        │
│ --force            -f             Process files that already have generated  │
│                                   metadata                                   │
│ --replace-caption                 Replace an existing caption                │
│ --replace-tags                    Replace existing tags instead of merging   │
│ --backup                                                                     │
│ --json                                                                       │
│ --quiet                                                                      │
│ --help                            Show this message and exit.                │
╰──────────────────────────────────────────────────────────────────────────────╯

```
