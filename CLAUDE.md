# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LARP character sheet generator. Reads `inputs/characters.csv` + `.docx` source files (synced from Google Docs), assembles Markdown profiles per character, then optionally converts to PDF.

## Commands

```bash
# Main generation (downloads from Google Drive + generates MD files)
python generator.py

# Dry run (validate inputs without overwriting)
python generator.py --dry-run

# Convert generated MD files to PDF (requires WeasyPrint + GTK3 on Windows)
python md_to_pdf.py

# Run tests
pytest

# Run a single test file
pytest test_utils.py
pytest test_generator.py

# Clean output/ and inputs/ (keeps characters.csv)
python cleanup.py
```

## Dependencies

- **Python 3.10+**
- **pandoc** — external binary, must be in PATH (converts .docx → markdown)
- **pip packages**: `requests`, `markdown`, `jinja2`, `weasyprint`
- **GTK3 runtime** — required by WeasyPrint on Windows for PDF generation

No `requirements.txt` exists — install manually.

## Architecture

```
inputs/
  characters.csv       # Main data table (UTF-8, comma-delimited)
  *.docx               # Source libraries (downloaded from Google Docs)
  *.md                 # Intermediate MD files created by pandoc from .docx

output/
  *.md                 # Generated character profiles (one per character)
  stats.txt            # Summary report
  pdf/                 # Generated PDFs

templates/
  character.html       # Jinja2 template used by md_to_pdf.py
```

### Data flow

1. **gdrive_client.py** — Downloads `.docx` and `.csv` from Google Drive (export URLs, no auth).
2. **utils.py** — `parse_markdown()` converts DOCX→MD via pandoc, then parses into `{ "H1": { "H2": "content", "__ROOT__": "...", "__ORIGINAL_H1__": "..." } }`. Keys are normalized (diacritics stripped from parenthetical/prefix codes like `C001`).
3. **generator.py** — Reads CSV rows, looks up text sections by `H1:H2` keys, injects cross-character role references, and writes output MD files.
4. **md_to_pdf.py** — Converts output MD files to PDF via WeasyPrint + Jinja2 template.

### Key lookup format

CSV columns `unit_role` and `circle_role` use `H1:H2` format (e.g. `Hvězdy:Kapitán`). If no colon, looks up `__ROOT__`. Missing keys produce `[MISSING: key]` in output and a console warning.

### GDOC_IDS in generator.py

Each Google Doc/Sheet has an ID hardcoded in `GDOC_IDS`. `csv` ID is `None` by default — CSV must be provided locally or the ID must be filled in.

### Team detection

`build_team_registry()` scans H1 headings in `cores.md` in order. Any heading containing "tým" (case-insensitive) becomes the current team; subsequent character headings inherit it.

## Code conventions

- Python 3.10+, English code and comments
- All files read/written as UTF-8
- Filenames sanitized: diacritics removed, spaces → underscores, non-alphanumeric removed (see `utils.sanitize_filename`)
