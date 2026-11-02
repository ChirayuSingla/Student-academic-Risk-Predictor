"""Start a local Streamlit server, check HTTP readiness, then stop it."""
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parents[1]


def main():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    result = {"python": sys.version.split()[0], "executable": sys.executable,
              "port": port, "status": "failed"}
    log_path = ROOT / "results" / "streamlit-smoke.log"
    log_path.parent.mkdir(exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
             "--server.address=127.0.0.1", f"--server.port={port}",
             "--server.headless=true", "--browser.gatherUsageStats=false"],
            cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            opener = build_opener(ProxyHandler({}))
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f"Streamlit exited with {process.returncode}; see {log_path}")
                try:
                    with opener.open(f"http://127.0.0.1:{port}/_stcore/health", timeout=2) as response:
                        assert response.status == 200 and response.read().strip() == b"ok"
                    with opener.open(f"http://127.0.0.1:{port}/", timeout=2) as response:
                        assert response.status == 200 and b"streamlit" in response.read().lower()
                    result.update(status="passed", health_http=200, app_http=200)
                    break
                except (URLError, TimeoutError):
                    time.sleep(0.25)
            else:
                raise TimeoutError("Streamlit did not become ready within 45 seconds.")
        except Exception as error:
            result["error"] = str(error)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    (ROOT / "results" / "streamlit-smoke.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
