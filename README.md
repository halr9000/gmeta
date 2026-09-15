# gmeta

Generate local VLM captions and tags, then write gallery-compatible XMP metadata to image files.

## Install

```bash
uv tool install git+https://github.com/halr9000/gmeta.git
```

## Usage

```bash
gmeta metadata ~/Pictures/AI_Art --recursive
```

By default, existing metadata is preserved. VLM tags are merged into existing tags. Captions are written to `XMP-dc:Description`; tags are written to `XMP-dc:Subject`, `XMP-digiKam:TagsList`, and `XMP-lr:HierarchicalSubject`.

```bash
# Preview without writing
gmeta metadata ~/Pictures/AI_Art --recursive --dry-run

# Reprocess files with existing generated metadata
gmeta metadata ~/Pictures/AI_Art --recursive --force

# Replace captions or tags explicitly
gmeta metadata ~/Pictures/AI_Art --recursive --force --replace-caption
gmeta metadata ~/Pictures/AI_Art --recursive --force --replace-tags

# Use a different OpenAI-compatible VLM server
gmeta metadata image.jpg --url http://127.0.0.1:8166
```

`--url` points to the base URL of an OpenAI-compatible server such as local `llama-server`; gmeta calls `/v1/chat/completions`.

## Development

```bash
uv sync
uv run pytest -q
uv run gmeta --help
```

## Publishing

Releases are published to PyPI from GitHub Actions using PyPI Trusted Publishing. Create a version tag after configuring the PyPI publisher for this repository.
