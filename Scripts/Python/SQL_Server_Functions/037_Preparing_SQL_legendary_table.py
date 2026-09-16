import subprocess
import sys
from pathlib import Path


SQL_CHECK_SCRIPT = Path(__file__).parent / "SQL_service_checking.py"
LOG_FILE = Path(__file__).parent / "sql_service_checking.log"


def main():

    result = subprocess.run(
        [sys.executable, str(SQL_CHECK_SCRIPT)],
        capture_output=True,
        text=True
    )

    # SQL_service_checking.py returned STATUS_OK
    assert result.returncode == 0, (
        "SQL service check failed. "
        f"See log file: {LOG_FILE}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())






    