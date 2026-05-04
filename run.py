"""Project-level launcher for backend and frontend."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    # Redirect to the new consolidated app entry point
    app_py = Path(__file__).resolve().parent / "app.py"
    runpy.run_path(str(app_py), run_name="__main__")
