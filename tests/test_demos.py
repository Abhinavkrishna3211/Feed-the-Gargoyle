import subprocess, sys, pathlib
import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app" / "python"


@pytest.mark.parametrize("name", ["game", "cues", "runner", "sensors", "voice", "costume"])
def test_module_selfcheck(name):
    r = subprocess.run([sys.executable, str(APP / f"{name}.py")], cwd=APP, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-800:]
