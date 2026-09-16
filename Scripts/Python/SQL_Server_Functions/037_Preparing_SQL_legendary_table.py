import subprocess
import sys
from pathlib import Path


SQL_CHECK_SCRIPT = Path(__file__).parent / "036_SQL_service_checking.py"
LOG_FILE = Path(__file__).parent / "sql_service_checking.log"

def main():

    result = subprocess.run(
        [sys.executable, str(SQL_CHECK_SCRIPT)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        LOG_FILE.write_text(
            result.stdout + "\n" + result.stderr,
            encoding="utf-8"
        )

    assert result.returncode == 0, (
        f"SQL service check failed. See log file: {LOG_FILE}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())






    