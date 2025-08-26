from datetime import datetime
import os
import sys


DEFAULT_EXCLUDED_FILE_EXT_LIST: list[str] = []

DEFAULT_EXCLUDED_DIR_LIST: list[str] = [
    "venv",
    ".git"
]


def get_Info_logging_string(content: str) -> str:
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - RUNTIME_INFO - {content}"


def get_excluded_dirs_abs_paths(base_dir: str, rel_exclude_dirs: list[str]) -> list[str]:
    excluded_abs_paths: list[str] = []
    for rel_dir in rel_exclude_dirs:
        abs_path = os.path.abspath(os.path.join(base_dir, rel_dir))
        excluded_abs_paths.append(abs_path)
    return excluded_abs_paths


def count_lines_in_file(file_path: str) -> int:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for _ in file)
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return sum(1 for _ in file)
        except Exception as e:
            print(get_Info_logging_string(f"Unable to read file {file_path}: {e}"))
            return 0
    except Exception as e:
        print(get_Info_logging_string(f"Error reading file {file_path}: {e}"))
        return 0


def count_lines_in_directory(
        dir_path: str, rel_exclude_dirs: list[str], exclude_file_exts: list[str]
    ) -> None:

    if not os.path.isdir(dir_path):
        print(get_Info_logging_string(f"Error: {dir_path} is not a valid directory"))
        return
    
    print(
        get_Info_logging_string(f"Counting lines in directory: {os.path.abspath(dir_path)}")
    )
    print(get_Info_logging_string("Mode: Recursively process all subdirectories"))
    print("-" * 60)
    
    total_lines: int = 0
    file_count: int = 0
    dir_count: int = 0
    
    excluded_dirs: list[str] = get_excluded_dirs_abs_paths(dir_path, rel_exclude_dirs)
    
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [ d for d in dirs if os.path.abspath(os.path.join(root, d)) not in excluded_dirs ]
        
        current_dir_lines: int = 0
        current_dir_files: int = 0
        
        for filename in files:
            file_path = os.path.join(root, filename)
            
            if any(filename.endswith(ext) for ext in exclude_file_exts):
                continue
                
            lines = count_lines_in_file(file_path)
            
            rel_path = os.path.relpath(file_path, dir_path)
            print(get_Info_logging_string(f"{rel_path}: {lines} lines"))
            
            current_dir_lines += lines
            current_dir_files += 1
            total_lines += lines
            file_count += 1
        
        if current_dir_files > 0:
            dir_count += 1
            if root != dir_path:
                rel_dir = os.path.relpath(root, dir_path)

                print(
                    get_Info_logging_string(
                        f"  [{rel_dir}/]: {current_dir_files} files, {current_dir_files} lines"
                    )
                )
                print("-" * 40)
    
    print("=" * 60)
    print(
        get_Info_logging_string(
            f"Total: {dir_count} directories, {file_count} files, {total_lines} lines"
        )
    )


def main() -> None:
    directory: str = "."
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if not arg.startswith('-'):
                directory = arg
            else:
                print(get_Info_logging_string(f"Unknown option: {arg}"))
                print(get_Info_logging_string("Usage: python script.py [dir_path]"))
                return
    
    count_lines_in_directory(
        directory, DEFAULT_EXCLUDED_DIR_LIST, DEFAULT_EXCLUDED_FILE_EXT_LIST
        )


if __name__ == "__main__":
    main()