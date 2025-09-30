## Local-event — Copilot instructions for editing and coding

These notes are targeted to AI coding agents working in this repository so you can be productive immediately.

- Workspace layout
  - `src/` contains runnable scripts: `har_parser.py` (the main parser) and `main.py` (simple entrypoint).
  - `src/Example.har` and `src/Example2.har` are sample HAR files used by the parser.
  - `requirements.txt` lists runtime dependencies (notably `haralyzer`).
  - `tests/` contains simple/unit test stubs (currently `tests/test_main.py`).

- Big-picture architecture and intent
  - This is a small script-based project whose purpose is to parse browser HAR files and extract Facebook GraphQL event names.
  - The primary logic lives in `src/har_parser.py`. It reads a HAR JSON, uses `haralyzer.HarParser` to iterate entries, filters for requests whose URL contains `api/graphql/` and method `POST`, and inspects response JSON for objects that look like Event nodes.
  - Output is printed to stdout. There is no web service or long-running process.

- Key functions & data flow (what to look at)
  - `parse_facebook_har(har_file_path)` in `src/har_parser.py` — input: HAR filepath; behaviour: loads JSON, collects GraphQL entries, parses response text, extracts event names via recursion.
  - `find_event_names(obj, found_events)` — recursive heuristic that detects dicts with `name` + (`eventUrl` or `__typename == 'Event'`) and appends names.
  - Example run: `parse_facebook_har('src/Example2.har')` is invoked at the bottom of `har_parser.py` (so running the file executes the parser).

- Project-specific patterns and conventions
  - Scripts are executed directly (not packaged). Running Python files prints results; functions return `None` on error and print messages instead of raising exceptions.
  - Heuristics are used to detect event structures (see `find_event_names`). Do not assume GraphQL shape is fixed — code already handles concatenated JSON lines and lists of objects.
  - Tests are minimal/placeholders. `tests/test_main.py` references a placeholder `your_function` — avoid changing tests unless you update the implementation accordingly.

- Dependencies and integration points
  - Uses the `haralyzer` package to read HAR data. Ensure `requirements.txt` is installed before running scripts.
  - No external network calls or credentials are present in the repo. HAR input files are local under `src/`.

- Developer workflows (commands to run here — PowerShell friendly)
  - Create and activate a local virtual environment (PowerShell):
    ```powershell
    # create a venv in the repo root
    python -m venv .venv

    # activate in PowerShell (dot-source the activation script)
    . .\.venv\Scripts\Activate.ps1

    # If script execution is blocked by ExecutionPolicy, use this process-scoped bypass
    # (runs in the same PowerShell session):
    #   powershell -ExecutionPolicy Bypass -Command ". .\\.venv\\Scripts\\Activate.ps1"

    # Fallback (cmd.exe):
    #   .\.venv\Scripts\activate
    ```
  - Install dependencies (inside the activated venv):
    ```powershell
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    ```
  - Run the parser (prints found events):
    ```powershell
    python src/har_parser.py
    ```
  - Run the simple main script:
    ```powershell
    python src/main.py
    ```
  - Run tests (note: tests are placeholders and may fail until implemented):
    ```powershell
    pytest tests
    # or
    python -m unittest discover -v
    ```

- Editing guidance and safe change patterns
  - When adding features, keep parse functions pure where possible: accept a filepath or JSON payload and return structured data (list of names) — current code prints directly.
  - Preserve existing heuristics for robustness to malformed responses (see the `try/except` blocks around JSON parsing in `har_parser.py`). If you improve parsing, keep a fallback that attempts line-splitting of concatenated JSON.
  - If you add new CLI flags or a small API, place them in `src/har_parser.py` (this project is script-first) and update `README.md` with usage examples.

- Tests and verification
  - Add unit tests under `tests/` that import functions from `src/har_parser.py` and assert on returned lists of event names.
  - Keep tests hermetic by using small sample HAR snippets (you can add fixtures under `tests/fixtures/`).

- Quick references to files to open first
  - `src/har_parser.py` — core logic and heuristics
  - `src/Example2.har` — example input used by the parser
  - `requirements.txt` — dependency: `haralyzer`
  - `tests/test_main.py` — current test layout and placeholders

If anything here is unclear or you'd like more detail (for example a suggested unit-test scaffold or converting the script to a small CLI), tell me which area to expand and I will update this file.
