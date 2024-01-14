from typing import List, Callable, IO
from transfer import rsync_transfer
import multiprocessing
import contextlib
import tempfile
import time
import os


def redirect_output(func: Callable, stdout_buffer: IO[str]) -> Callable:
    """
    Redirecting stdout and stderr of specific function.
    """

    def inner(*args, **kwargs):
        with contextlib.redirect_stdout(stdout_buffer):
            result = func(*args, **kwargs)
        return result

    return inner


class MultiRsyncProcess(object):
    """
    Class that represent a process of rsync transfer,
    which his stdout is going to be redirect to self,stdout_buffer.
    """

    def __init__(self, src_path: str, dest_path: str):
        self.src_path = src_path
        self.dest_path = dest_path
        self.stdout_buffer = tempfile.TemporaryFile(mode="r+")
        self.process = multiprocessing.Process(name=src_path,
                                               target=redirect_output(rsync_transfer,
                                                                      self.stdout_buffer),
                                               args=(src_path, dest_path))
        self.process.start()

    def get_process_output(self):
        """
        Get the last output from the stdout of the process.
        """
        output = [self.process.name]
        self.stdout_buffer.seek(0)
        stdout_data = self.stdout_buffer.readlines()
        output.append(stdout_data.pop().strip() if stdout_data else '')
        return "\n".join(output)


def multi_rsync_transfer(source_paths: List[str], destination_paths: List[str]) -> None:
    """
    Transfer multi files from source_paths to destination_paths using rsync command.
    (The function connects the source path to the destination path by list index)
    :param source_paths: list of your srouce paths
    :param destination_paths: list of your destination paths
    """
    if len(source_paths) != len(destination_paths):
        raise ValueError("Expect source_paths and destination_paths to be with the same size!")

    processes = []
    for src_path, dest_path in zip(source_paths, destination_paths):
        processes.append(MultiRsyncProcess(src_path, dest_path))

    while list(filter(lambda rsync_process: rsync_process.process.is_alive(), processes)):
        for rsync_process in processes:
            print(rsync_process.get_process_output())
        time.sleep(0.5)
        os.system("clear")

    for rsync_process in processes:
        print(rsync_process.get_process_output())


def main():
    multi_rsync_transfer(["/tmp/test/t4", "/tmp/test/t2", "/tmp/test/t3"],
                         ["/tmp/test2/t1", "/tmp/test2/t2", "/tmp/test2/t3"])


if __name__ == '__main__':
    main()
