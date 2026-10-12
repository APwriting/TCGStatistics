import subprocess
import sys
from pathlib import Path

import MTG_SQL as Msql

SQL_CHECK_SCRIPT = Path(__file__).parent / "036_SQL_service_checking.py"
LOG_FILE = Path(__file__).parent / "sql_service_checking.log"

def main():
    if 0:
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
    Msql.check_cluster_availability(file_name = SQL_CHECK_SCRIPT, log_file = LOG_FILE)



    return 1


if __name__ == "__main__":
    sys.exit(main())






    