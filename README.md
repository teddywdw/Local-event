# Local-event

## Overview
This small script-based project parses browser HAR files and extracts (Facebook) GraphQL event names. The parser is in `src/har_parser.py` and example HAR files live in `src/`.

## Project structure
```
Local-event
├── src
│   ├── har_parser.py
│   ├── main.py
│   └── Example2.har
├── tests
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Getting started (PowerShell)

### Prerequisites
Install Python 3.8+ on your machine.

### Create and activate a venv (PowerShell)
```powershell
# from the repository root
python -m venv .venv

# Activate in PowerShell (dot-source the activation script)
. .\.venv\Scripts\Activate.ps1

# If activation is blocked by ExecutionPolicy, use this one-shot bypass in the same session:
# powershell -ExecutionPolicy Bypass -Command ". .\.venv\Scripts\Activate.ps1"

# Fallback (cmd.exe):
# .\.venv\Scripts\activate
```

### Install dependencies (inside the activated venv)
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Run the parser
The parser prints found event names for `src/Example2.har` by default (see bottom of `src/har_parser.py`):
```powershell
python src/har_parser.py
```

### Run tests
This repo currently contains placeholder tests. After activating the venv and installing dependencies you can run:
```powershell
pytest -q
# or, if you prefer built-in discovery:
python -m unittest discover -v
```

## Contributing
PRs and issues welcome. If you add features, prefer to keep parsing functions pure (accept file path or JSON and return structured data) so they are easy to test.

## Developer setup (one-liner)
After cloning, to get a development environment with linters and hooks installed (PowerShell):
```powershell
# from repo root
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
pre-commit install
```

Or run the included helper:
```powershell
.\scripts\setup-dev.ps1
```
