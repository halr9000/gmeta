# gmeta

`gmeta` generates captions and tags with a vision-language model (VLM), then writes them into image metadata. It is designed for local, OpenAI-compatible inference servers and preserves existing metadata by default.

## What it changes

For each supported image, gmeta can write:

- Caption → `XMP-dc:Description`
- Tags → `XMP-dc:Subject`
- Tags → `XMP-digiKam:TagsList`
- Tags → `XMP-lr:HierarchicalSubject`

Existing tags are merged with generated tags. Existing captions are preserved. Other metadata is left alone.

## Requirements

- Python 3.11 or newer
- ExifTool available on `PATH`
- An OpenAI-compatible VLM server for caption generation

The VLM server can be local or remote. gmeta sends one multimodal request to its `/v1/chat/completions` endpoint for each image.

## Install

Install the latest development version directly from GitHub:

```bash
uv tool install git+https://github.com/halr9000/gmeta.git
```

After installation, check the command:

```bash
gmeta --help
gmeta --version
```

## Basic use

The command accepts image files and directories. A directory is processed non-recursively unless `--recursive` is supplied.

```bash
# One image
gmeta metadata image.jpg

# All supported images directly in a directory and its subdirectories
gmeta metadata photos/ --recursive
```

The default prompt is the prompt used in the successful LFM evaluation:

```text
Caption this image using the required JSON schema.
```

That prompt is added as the user message. gmeta always supplies a separate system prompt with the tested grounding rules and JSON schema. Passing `--prompt` changes the user request; it does not remove those system rules.

## Preview and update policy

Start with a dry run:

```bash
gmeta metadata photos/ --recursive --dry-run
```

By default, gmeta skips files that already contain both a caption and tags. Use `--force` to run inference for those files again:

```bash
gmeta metadata photos/ --recursive --force
```

`--force` permits reprocessing; it does not overwrite existing fields by itself. Use the replacement flags when that is the intended result:

```bash
# Re-run inference and replace an existing caption
gmeta metadata photos/ --recursive --force --replace-caption

# Re-run inference and replace tags instead of merging them
gmeta metadata photos/ --recursive --force --replace-tags
```

These controls are independent. For example, `--force --replace-tags` reruns inference, preserves an existing caption, and replaces only the tags.

## VLM connection

`--url` is the base URL of the OpenAI-compatible server. gmeta appends `/v1/chat/completions`.

```bash
gmeta metadata image.jpg --url http://127.0.0.1:8080
```

Use `--model` when the server needs a model identifier:

```bash
gmeta metadata image.jpg --url http://127.0.0.1:8080 --model my-vision-model
```

Use `--prompt` for a task-specific addition while keeping gmeta's grounding and JSON requirements:

```bash
gmeta metadata image.jpg \
  --prompt 'Pay particular attention to visible text and the dominant color palette.'
```

## Output and logging

Normal status and error messages are written to stderr. Structured per-file results go to stdout with `--json`:

```bash
gmeta metadata photos/ --recursive --json > results.json
```

Use `--quiet` to suppress ordinary per-file status lines. Errors are still logged, and the command exits nonzero if any file fails.

For a safety copy before writing:

```bash
gmeta metadata photos/ --recursive --backup
```

## Parameters

The parameter reference is generated from the live CLI help:

```bash
uv run python scripts/generate_docs.py
```

See [`docs/parameters.md`](docs/parameters.md).

## Development

```bash
git clone https://github.com/halr9000/gmeta.git
cd gmeta
uv sync
uv run pytest -q
uv run gmeta metadata --help
uv run python scripts/generate_docs.py
uv build
```

## Publishing releases

The repository includes a GitHub Actions workflow for PyPI Trusted Publishing. A maintainer configures the repository as a trusted publisher in PyPI, then publishes a release by pushing a version tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

The workflow builds the source distribution and wheel, then publishes them without storing a long-lived PyPI API token in GitHub.

## License

MIT
