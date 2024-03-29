from typing import List
import subprocess
import sys
import os


def _get_transfer_command(src_path: str, dest_path: str) -> List[str]:
    """
    rsync command for Transfer all file/folder inside src_path to dest_path.
    """
    return ["rsync",
            "-ah",
            "--info=progress2",
            "--bwlimit=500",
            src_path if src_path.endswith("/") else src_path + "/",
            dest_path]


def rsync_transfer(source_path: str, destination_path: str) -> int:
    """
    Transfer files using rsync command.
    :return: the returncode of the rsync transfer.
    """
    os.makedirs(destination_path, exist_ok=True)

    with (subprocess.Popen(
            _get_transfer_command(source_path, destination_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
    ) as process):
        for line in process.stdout:
            print(line.strip(), end='\r', flush=True)

        for line in process.stderr:
            print(line.strip())

    if process.returncode == 0:
        print("\nTransfer completed successfully!")
    sys.stdout.flush()

    return process.returncode
