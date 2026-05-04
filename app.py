"""One-command launcher for the Rice AI backend and frontend."""

import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn
from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_DIR / "ui"


def _npm_command() -> str | None:
    """Return the npm executable for this platform."""
    if os.name == "nt":
        return shutil.which("npm.cmd") or shutil.which("npm")
    return shutil.which("npm")


def _start_frontend(frontend_url: str, api_url: str) -> subprocess.Popen | None:
    """Start the Vite dev server for the React UI."""
    npm = _npm_command()
    if npm is None:
        print("[WARN] npm was not found. Backend will run, but frontend will not start.")
        return None

    if not FRONTEND_DIR.exists():
        print(f"[WARN] Frontend folder not found: {FRONTEND_DIR}")
        return None

    env = os.environ.copy()
    env["VITE_API_URL"] = api_url

    host = frontend_url.split("://", 1)[-1].split(":", 1)[0]
    port = frontend_url.rsplit(":", 1)[-1]

    print(f"[*] Starting frontend at {frontend_url}...")
    return subprocess.Popen(
        [npm, "run", "dev", "--", "--host", host, "--port", port],
        cwd=FRONTEND_DIR,
        env=env,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )


def _stop_frontend(process: subprocess.Popen | None) -> None:
    """Stop the Vite dev server when the backend exits."""
    if process is None or process.poll() is not None:
        return

    print("[*] Stopping frontend...")
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        process.terminate()


def _backend_is_healthy(api_url: str) -> bool:
    """Return True if an existing backend is already serving health checks."""
    health_url = f"{api_url.rstrip('/')}/health"
    try:
        with urllib.request.urlopen(health_url, timeout=3) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


if __name__ == "__main__":
    load_dotenv()
    os.chdir(PROJECT_DIR)

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    api_url = os.getenv("VITE_API_URL", f"http://127.0.0.1:{port}/api")
    frontend_url = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")

    os.environ["FRONTEND_URL"] = frontend_url

    backend_already_running = _backend_is_healthy(api_url)
    if backend_already_running:
        print(f"[*] Reusing running backend at {api_url}")

    frontend_process = _start_frontend(frontend_url, api_url)
    print(f"[*] UI: {frontend_url}")
    print(f"[*] API: {api_url}")

    try:
        time.sleep(2)
        if os.getenv("OPEN_BROWSER", "true").lower() == "true":
            webbrowser.open(frontend_url)

        if backend_already_running:
            print("[*] Press Ctrl+C to stop the frontend launcher.")
            while True:
                time.sleep(1)
        else:
            print(f"[*] Starting backend at http://{host}:{port}...")
            sys.path.insert(0, str(PROJECT_DIR))
            uvicorn.run(
                "api.main:app",
                host=host,
                port=port,
                reload=False,
                app_dir=str(PROJECT_DIR)
            )
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    except Exception as e:
        print(f"\n[ERROR] Backend crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        _stop_frontend(frontend_process)
