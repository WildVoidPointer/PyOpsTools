from collections.abc import Iterable
from datetime import datetime
from typing import Optional
import hashlib
import secrets
import time
import sys
import os


class FnameToHashRuntimeStatus:
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
            f"{datetime.now()} - INFO: \033[32m{op_s_count}\033[0m files were renamed successfully.\n"
            f"{datetime.now()} - INFO: \033[31m{op_f_count}\033[0m files failed to be renamed."
        )

    @staticmethod
    def get_rename_failed_files(files: Iterable[str]) -> None:
        if not isinstance(files, Iterable):
            return
        print("\033[31mRenameFailedList:\033[0m")
        for file in files:
            print(f"    {file}")


def get_all_files_to_tuple(dirpath: str) -> tuple[str, ...]:
    """Extract all files from the specified path.

    Args:
        dirpath: A string indicating the path of a directory

    Returns:
        Returns a tuple of all files
    
    Raises:
        Raises `ValueError` if the passed argument is invalid
    """
    if not is_effective_string(dirpath) or not os.path.isdir(dirpath) or \
        not os.access(dirpath, os.X_OK | os.R_OK | os.W_OK):
        raise ValueError(f"The method {__name__} parameter is invalid")
    
    files_list: list[str] = []
    for dirpath, _, filenames in os.walk(dirpath):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            absolute_path = os.path.abspath(filepath)
            files_list.append(absolute_path)
    return tuple(files_list)


def is_effective_string(string: str) -> bool:
    """Determine string validity"""
    return isinstance(string, str) and string != ""


def get_current_timestamp() -> str:
    """Get the current time string in the format of `%Y-%m-%d %H:%M:%S.%f`

    Args:
        None
    
    Returns:
        Return a string in the format of %Y-%m-%d %H:%M:%S.%f
    
    Raises:
        None
    """
    return datetime.now().strftime(r"%Y-%m-%d %H:%M:%S.%f")


def get_current_random_salt() -> str:
    """Get random string of 16 length by secrets-lib

    Args:
        None
    
    Returns:
        Returns a random string of 16 length
    
    Raises:
        None
    """
    return secrets.token_hex(nbytes=16)


def get_current_file_hashcode(
        fpath: str, timestamp: str, random_salt: str, hash_type: str = 'sha1'
        ) -> str:
    """Generate and return a hash string with the file path, timestamp, and random salt

    Args:
        fpath: A valid file path.
        timestamp: A time string in the format of %Y-%m-%d %H:%M:%S.%f
        random_salt: a random string
        hash_type: A hash encryption type
    
    Returns:
        Returns a hashcode string of 40 length (sha1)
    
    Raises:
        Raises `ValueError` if the passed argument is invalid or 
        the hash encryption type is not supported
    """
    
    if (
        not is_effective_string(fpath) or not is_effective_string(timestamp) or 
        not is_effective_string(random_salt) or not is_effective_string(hash_type) or
        not os.path.isfile(fpath)
        ):
        raise ValueError(f"The method {__name__} parameter is invalid")
    
    file_hash = hashlib.new(hash_type)
    chunk_data = fpath + timestamp + random_salt
    file_hash.update(chunk_data.encode('utf-8'))
    return file_hash.hexdigest().lower()


def set_filename_to_hashcode(fpath: str, hashcode: str) -> bool:
    """Set the file name to the hashcode passed in.

    Args:
        fpath: A valid file path.
        hashcode: A vaild string
    
    Returns:
        Returns a Boolean value indicating execution
    
    Raises:
        None 
    """

    if (
        not is_effective_string(fpath) or not os.path.isfile(fpath) 
        or not is_effective_string(hashcode)
        ):

        return False
    
    _fpath, _fname = os.path.split(fpath)
    new_fname: str = hashcode + os.path.splitext(_fname)[1]
    new_fpath = os.path.join(_fpath, new_fname)

    if os.path.exists(new_fpath):
        return False
    
    try:
        os.rename(fpath, new_fpath)
    except OSError as e:
        print(FnameToHashRuntimeStatus.get_error_message(str(e)))
        return False

    return True


def rename_operation_executor(dirpath: str) -> tuple[int, int, int, tuple[str, ...]]:
    """Batch file renaming is performed.

    Args:
        dirpath: A string indicating the path of a directory.
    
    Returns:
        Returns a tuple of 4, in order, the number of scanned files,
        the number of successful operations, the number of failed operations, 
        and the sequence of failed operations.
    
    Raises:
        None
    """
    if not is_effective_string(dirpath) or not os.path.isdir(dirpath):

        print(
            FnameToHashRuntimeStatus.get_error_message(f"The method {__name__} parameter is invalid")
        )
        return 0, 0, 0, tuple()
    
    fpaths: Optional[tuple[str, ...]] = None
    try: 
        fpaths = get_all_files_to_tuple(dirpath)
    except ValueError as e:
        print(FnameToHashRuntimeStatus.get_error_message(str(e)))
        sys.exit(1)

    op_success_count: int = 0
    op_failure_count: int = 0
    op_failure_files: list[str] = []

    for path in fpaths:
        _current_timestamp = get_current_timestamp()
        _current_salt = get_current_random_salt()

        _current_fhash = get_current_file_hashcode(
            fpath=path, timestamp=_current_timestamp, random_salt=_current_salt
        )

        try: 
            _rename_flag: bool = set_filename_to_hashcode(path, _current_fhash)
            if _rename_flag:
                op_success_count += 1
            else:
                op_failure_count += 1
                op_failure_files.append(path)
        except ValueError as e:
            op_failure_count += 1
            op_failure_files.append(path)
            print(FnameToHashRuntimeStatus.get_error_message(str(e)))
    return len(fpaths), op_success_count, op_failure_count, tuple(op_failure_files)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\033[31mUsage: python script.py <directory_path>. \033[0m")
        sys.exit(1)

    start_time: float = time.time()
    dirpath: str = sys.argv[1]
    
    _scan_fcount, _op_s, _op_f, _op_f_files = rename_operation_executor(dirpath=dirpath)
    print(FnameToHashRuntimeStatus.get_files_counter_message(_scan_fcount))
    print(FnameToHashRuntimeStatus.get_op_result_message(_op_s, _op_f))
    FnameToHashRuntimeStatus.get_rename_failed_files(_op_f_files)
    print(f"Running time: \033[33m{time.time()-start_time}\033[0ms")
    print(f"\033[32mComplete !\n\033[0m")
