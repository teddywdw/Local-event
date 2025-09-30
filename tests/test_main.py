import importlib.util
from pathlib import Path


def load_main_module():
    # Load src/main.py as a module without requiring a package import
    repo_root = Path(__file__).resolve().parents[1]
    main_path = repo_root / "src" / "main.py"
    spec = importlib.util.spec_from_file_location("local_main", str(main_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_prints_hello(capsys):
    mod = load_main_module()
    assert hasattr(mod, "main")
    # Call main() and capture stdout
    mod.main()
    captured = capsys.readouterr()
    assert "Hello, World" in captured.out
