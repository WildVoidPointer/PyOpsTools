from collections.abc import Iterable
from datetime import datetime
import shutil
import sys
import os


class FilesCleanerLogger:
    """Provides a series of static methods to highlight run-time status with simple logs"""
    @staticmethod
    def get_error_message(location: str = "") -> str:
        return f"\033[31m{datetime.now()} - ERROR: {location} \033[0m"
    
    @staticmethod
    def get_files_counter_message(count: int = 0) -> str:
        return f"{datetime.now()} - INFO: \033[33m{count}\033[0m files have been scanned."
    
    @staticmethod
    def get_op_result_message(moved_count: int = 0, rename_count: int = 0) -> str:
        return (
            f"{datetime.now()} - INFO: \033[32m{moved_count}\033[0m files were moved successfully.\n"
            f"{datetime.now()} - INFO: \033[31m{rename_count}\033[0m files were renamed."
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


def is_apple_double_file(fname: str) -> bool:
    return fname.startswith("._")


def capture_apple_double_files(path: str) -> tuple[str, ...]:

    if not _is_effective_dirpath(path=path):
        print(
            FilesCleanerLogger.get_error_message(
                "The specified directory does not exist or is inaccessible"
            )
        )
        sys.exit(1)
    
    abspath = os.path.abspath(path)

    apple_double_files: list[str] = []

    for dirpath, _, files in os.walk(abspath):
        for file in files:
            if is_apple_double_file(file):
                apple_double_files.append(os.path.join(dirpath, file))

    return tuple(apple_double_files)


def move_apple_double_files(
    root_path: str, adfiles: Iterable[str], is_default_target: bool = True,
    target: str = 'AppleDoubleFiles'
) -> tuple[str, ...] | None:
    
    if not _is_effective_dirpath(root_path) or not isinstance(adfiles, Iterable):
        print(
            FilesCleanerLogger.get_error_message(
                "The AppleDouble files cannot be moved. \
                Make sure you pass in the correct parameters"
            )
        )
        sys.exit(2)

    root_path = os.path.abspath(root_path)
    
    if is_default_target:
        dir_name = target + "-" + datetime.now().strftime(r"%Y-%m-%d-%H-%M-%S-%f")
        collect_space: str = os.path.join(root_path, dir_name)

    else:
        if not _is_effective_dirpath(target):
            print(
                FilesCleanerLogger.get_error_message(
                    "The AppleDouble files cannot be moved. \
                    Make sure you pass in the correct parameters"
                )
            )
            sys.exit(2)

        collect_space = os.path.abspath(target)
    
    if not os.path.exists(collect_space) and len(tuple(adfiles)) != 0:
        os.mkdir(collect_space)

    renamed_files: list[str] = []

    new_name_tag: str = "same"

    new_name_count: int = 1
    
    for file in adfiles:
        fname: str = os.path.basename(file)

        if os.path.exists(os.path.join(collect_space, fname)):
            new_name: str = os.path.join(
                os.path.dirname(file), 
                "-" + fname + "-" + new_name_tag + str(new_name_count)
            )
            os.rename(file, new_name)
            file = new_name
            new_name_count += 1
        
        shutil.move(file, collect_space)
    
    if len(renamed_files) == 0:
        return None
    else:
        return tuple(renamed_files)


def apple_double_files_collector(
    dirpath: str, is_default_target: bool = True, target: str | None = None
) -> None:
    
    apple_double_files: tuple[str, ...] = capture_apple_double_files(dirpath)
    renamed_list: tuple[str, ...] | None  = None

    if not is_default_target and target != None:
        renamed_list = move_apple_double_files(dirpath, apple_double_files, is_default_target, target)
    else:   
        renamed_list = move_apple_double_files(dirpath, apple_double_files)

    all_file_num: int = len(apple_double_files)

    if renamed_list is not None:
        not_moved_num: int = len(renamed_list)
        moved_num: int = all_file_num - not_moved_num
    else:
        moved_num = all_file_num
        not_moved_num = 0
    
    print(
        FilesCleanerLogger.get_files_counter_message(all_file_num)
    )

    print(
        FilesCleanerLogger.get_op_result_message(moved_num, not_moved_num)
    )

    if renamed_list is not None:
        FilesCleanerLogger.get_moved_failed_files(renamed_list)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\033[31mUsage: python script.py <directory_path>. \033[0m")
        sys.exit(3)
    
    apple_double_files_collector(sys.argv[1])
