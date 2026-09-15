from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
help_text = subprocess.run(
    ["uv", "run", "gmeta", "metadata", "--help"],
    cwd=root,
    check=True,
    capture_output=True,
    text=True,
).stdout
body = """# Parameter reference

Generated from the live CLI help. Regenerate with:

```bash
uv run python scripts/generate_docs.py
```

The `--prompt` value is added as the user message. The tested grounding and JSON rules remain in the system prompt.

## `gmeta metadata`

```text
""" + help_text + """```
"""
(root / "docs" / "parameters.md").write_text(body)
