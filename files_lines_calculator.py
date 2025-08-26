import os
import sys
from datetime import datetime


EXCLUDED_FILE_EXT_LIST = []


EXCLUDED_DIR_LIST = [
    "venv"
]


def get_Info_logging(content):
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO - {content}"


def get_excluded_dirs_abs_paths(base_dir):
    excluded_abs_paths = []
    for rel_dir in EXCLUDED_DIR_LIST:
        abs_path = os.path.abspath(os.path.join(base_dir, rel_dir))
        excluded_abs_paths.append(abs_path)
    return excluded_abs_paths


def count_lines_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for _ in file)
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return sum(1 for _ in file)
        except Exception as e:
            print(get_Info_logging(f"Unable to read file {file_path}: {e}"))
            return 0
    except Exception as e:
        print(get_Info_logging(f"Error reading file {file_path}: {e}"))
        return 0


def count_lines_in_directory(directory_path):
    if not os.path.isdir(directory_path):
        print(get_Info_logging(f"Error: {directory_path} is not a valid directory"))
        return
    
    print(get_Info_logging(f"Counting lines in directory: {os.path.abspath(directory_path)}"))
    print(get_Info_logging("Mode: Process current directory only"))
    print("-" * 60)
    
    total_lines = 0
    file_count = 0
    
    excluded_dirs = get_excluded_dirs_abs_paths(directory_path)
    
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        if os.path.isdir(file_path):
            if file_path in excluded_dirs:
                continue
        else:
            if any(filename.endswith(ext) for ext in EXCLUDED_FILE_EXT_LIST):
                continue
            
            lines = count_lines_in_file(file_path)
            print(get_Info_logging(f"{filename}: {lines} lines"))
            
            total_lines += lines
            file_count += 1
    
    print("=" * 60)
    print(get_Info_logging(f"Total: {file_count} files, {total_lines} lines"))


def main():
    directory = "."
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if not arg.startswith('-'):
                directory = arg
            else:
                print(get_Info_logging(f"Unknown option: {arg}"))
                print(get_Info_logging("Usage: python script.py [dir_path]"))
                return
    
    count_lines_in_directory(directory)

if __name__ == "__main__":
    main()
