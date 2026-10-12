

import subprocess
import sys
from pathlib import Path








def check_cluster_availability(file_name, log_file ):
    #Function takes in 
    #file_name = script to check SQL service availability
    result = subprocess.run(
        [sys.executable, str(file_name)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        log_file.write_text(
            result.stdout + "\n" + result.stderr,
            encoding="utf-8"
        )

    assert result.returncode == 0, (
        f"SQL service check failed. See log file: {log_file}"
    )

    


def main():
    pass


if __name__ == "__main__":
    sys.exit(main())