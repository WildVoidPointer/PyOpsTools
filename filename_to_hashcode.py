from datetime import datetime
import hashlib
import secrets
import random
import time
import sys
import os


def get_file_hashcode(path: str, hash_type: str = 'sha1') -> str | None:
    if isinstance(path, str) and os.path.isfile(path) and isinstance(hash_type, str) \
            and path != '' and hash_type != '':
        file_meta_hash = hashlib.new(hash_type)
        file_size: int = os.path.getsize(path)
        file_changed_time: str = time.strftime('%Y-%m-%d %H:%M:%S', 
                                               time.localtime(os.path.getmtime(path)))
        chunk_data: str = str(file_size) + file_changed_time
        file_meta_hash.update(chunk_data.encode('utf-8'))
        return file_meta_hash.hexdigest().lower()
    return None


def generate_salt(length: int = 16) -> str:
    salt = secrets.token_hex(length)
    return salt


def get_current_time_hashcode(hash_type: str = 'sha1') -> str:
    time_hash = hashlib.new(hash_type)
    time_stamp: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    random_flag: int = random.randint(random.randint(0, 250000), random.randint(250001, 500000))
    seed: str = time_stamp + str(random_flag) + generate_salt()
    time_hash.update(seed.encode('utf-8'))
    return time_hash.hexdigest().lower()


def count_files(path: str) -> int:
    total_files = 0
    if isinstance(path, str) and os.path.isdir(path) and path != '':
        for _, _, filenames in os.walk(path):
            total_files += len(filenames)
    return total_files


def files_rename_executor(path: str) -> None:
    if isinstance(path, str) and os.path.isdir(path) and path != '':
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                new_file_name = get_file_hashcode(file_path) + os.path.splitext(filename)[1]
                new_path = os.path.join(dirpath, new_file_name)
                if os.path.exists(new_path):
                    new_path = os.path.join(dirpath, get_current_time_hashcode() + os.path.splitext(filename)[1])
                try:
                    os.rename(file_path, new_path)
                except OSError:
                    print(f"    Error renaming file {file_path} \n      to {new_path}")
        print("    Succeeded in batch renaming hashcode")


if __name__ == "__main__":
    start_time: float = time.time()
    if len(sys.argv) < 2:
        print("    Usage: python script.py <directory_path>")
        sys.exit(1)

    path: str = sys.argv[1]
    print(f"    The target directory to be processed is: {path}")
    print(f"    \033[31m{count_files(path=path)}\033[0m files have been scanned")
    files_rename_executor(path=path)
    print(f"    Running time: {time.time()-start_time}")
    print('    \033[32mComplete !\033[0m')
