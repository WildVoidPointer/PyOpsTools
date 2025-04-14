from collections.abc import Iterable
from datetime import datetime
import shutil
import sys
import os


class FilesCleanerStatus:
    """Provides a series of static methods to highlight run-time status with simple logs"""
    @staticmethod
    def get_error_message(location: str = "") -> str:
        return f"\033[31m{datetime.now()} - ERROR: {location} \033[0m"
    
    @staticmethod
    def get_files_counter_message(count: int = 0) -> str:
        return f"{datetime.now()} - INFO: \033[33m{count}\033[0m files have been scanned."
    
    @staticmethod
    def get_op_result_message(op_s_count: int = 0, op_f_count: int = 0) -> str:
        return (
            f"{datetime.now()} - INFO: \033[32m{op_s_count}\033[0m files were moved successfully.\n"
            f"{datetime.now()} - INFO: \033[31m{op_f_count}\033[0m files failed to be moved."
        )
    
    @staticmethod
    def get_moved_failed_files(files: Iterable[str]) -> None:
        if not isinstance(files, Iterable):
            return
        print("\033[31mMoveFailedList:\033[0m")
        for file in files:
            print(f"    {file}")
    

def _is_effective_dirpath(path: str) -> bool:
    return isinstance(path, str) and os.path.isdir(path) and path != "" \
            and os.access(path, os.X_OK | os.R_OK | os.W_OK)


def _is_apple_double_file(fname: str) -> bool:
    return fname.startswith("._")


def _collect_apple_double_files(path: str) -> tuple[str, ...]:
    if not _is_effective_dirpath(path=path):
        print(
            FilesCleanerStatus.get_error_message(
                "The specified directory does not exist or is inaccessible"
            )
        )
        sys.exit(1)
    
    path = os.path.abspath(path)

    _apple_double_files: list[str] = []
    for dirpath, _, files in os.walk(path):
        for file in files:
            if _is_apple_double_file(file):
                _apple_double_files.append(os.path.join(dirpath, file))
    return tuple(_apple_double_files)


def _move_apple_double_files(root_path: str, adfiles: tuple[str, ...],
                             is_default_target: bool = True,
                             mv_target: str = 'AppleDoubleFiles') -> tuple[str, ...] | None:
    
    if not _is_effective_dirpath(root_path) or not isinstance(adfiles, tuple):
        print(
            FilesCleanerStatus.get_error_message(
                "The AppleDouble files cannot be moved. Make sure you pass in the correct parameters"
            )
        )
        sys.exit(2)

    root_path = os.path.abspath(root_path)
    
    if is_default_target:
        mv_target = mv_target + "-" + datetime.now().strftime(r"%Y-%m-%d-%H-%M-%S-%f")
        _mv_target: str = os.path.join(root_path, mv_target)

    else:
        if not _is_effective_dirpath(mv_target):
            print(
            FilesCleanerStatus.get_error_message(
                "The AppleDouble files cannot be moved. Make sure you pass in the correct parameters"
            )
        )
        sys.exit(2)

        _mv_target = os.path.abspath(mv_target)
    
    if not os.path.exists(_mv_target):
        os.mkdir(_mv_target)

    _not_moved_files: list[str] = []
    
    for file in adfiles:
        fname: str = os.path.basename(file)

        if os.path.exists(os.path.join(_mv_target, fname)):
            _not_moved_files.append(file)
        else:
            shutil.move(file, _mv_target)
    
    if len(_not_moved_files) == 0:
        return None
    else:
        return tuple(_not_moved_files)


def apple_double_files_collector(dirpath: str,
                               is_default_target: bool = True,
                               target: str | None = None
                            ) -> None:
    apple_double_files: tuple[str, ...] = _collect_apple_double_files(dirpath)
    move_res: tuple[str, ...] | None  = None

    if not is_default_target and target != None:
        move_res = _move_apple_double_files(dirpath, apple_double_files, is_default_target, target)
    else:   
        move_res = _move_apple_double_files(dirpath, apple_double_files)

    _all_file_num: int = len(apple_double_files)

    if move_res is not None:
        _op_f_num: int = len(move_res)
        _op_s_num: int = _all_file_num - _op_f_num
    else:
        _op_s_num = _all_file_num
        _op_f_num = 0
    
    print(
        FilesCleanerStatus.get_files_counter_message(_all_file_num)
    )

    print(
        FilesCleanerStatus.get_op_result_message(_op_s_num, _op_f_num)
    )

    if move_res is not None:
        FilesCleanerStatus.get_moved_failed_files(move_res)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\033[31mUsage: python script.py <directory_path>. \033[0m")
        sys.exit(3)
    
    apple_double_files_collector(sys.argv[1])
