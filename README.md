# Local-event

## Overview
This project provides tools for parsing browser HAR files and extracting Facebook GraphQL event data. The parser module is located in `src/parser/` and a web interface will be available in `src/web/`.

## Project structure
```
Local-event
├── src/
│   ├── parser/           # HAR parsing utility module
│   │   ├── har_parser.py # Main parser logic
│   │   ├── Example2.har  # Sample HAR file
│   │   └── __init__.py   # Module interface
│   ├── web/              # Web interface (planned)
│   │   └── __init__.py
│   ├── main.py           # Simple entry point
│   └── __init__.py
├── tests/
│   └── test_main.py
├── requirements.txt
├── DATA_CONTRACT.md      # JSON output schema
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
The parser extracts events from HAR files with both text and JSON output formats:
```powershell
# Text output (human-readable, default)
python src/parser/har_parser.py --format text

# JSON output (for programmatic use)
python src/parser/har_parser.py --format json

# Specify a different HAR file
python src/parser/har_parser.py --har path/to/your/file.har --format json

# Debug mode for troubleshooting
python src/parser/har_parser.py --debug --format text
```

### Use as a Python module
```python
# Import the parser module
from src.parser import main, extract_event_info

# Get structured event data
events = main(debug=False, har_path="src/parser/Example2.har", output_format="json")
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
