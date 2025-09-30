import sys
from pathlib import Path

# Ensure the repository root (project root) is on sys.path so tests can import `src` as a package
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
