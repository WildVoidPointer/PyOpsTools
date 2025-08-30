from datetime import datetime
import argparse
import os


def get_Info_logging_string(content: str) -> str:
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - RUNTIME_INFO - {content}"


def get_all_subdirectories(root_dir: str) -> list[str]:
    """
    Recursively collect all subdirectories within the root directory.
    
    Args:
        root_dir: Path to the root directory
        
    Returns:
        List of absolute paths to all subdirectories
    """
    if not os.path.exists(root_dir):
        print(get_Info_logging_string(f"Root directory '{root_dir}' does not exist"))
        return []
    
    if not os.path.isdir(root_dir):
        print(get_Info_logging_string(f"'{root_dir}' is not a directory"))
        return []
    
    subdirectories = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        subdirectories.append(dirpath)
    
    return subdirectories


def rename_files_in_directory(directory_path: str) -> int:
    """
    Rename all files in the given directory with pattern: directory_name-number.extension.
    
    Args:
        directory_path: Absolute path to the directory containing files to rename
        
    Returns:
        Number of files successfully renamed
    """
    if not os.path.exists(directory_path):
        print(get_Info_logging_string(f"Directory '{directory_path}' does not exist"))
        return 0
    
    if not os.path.isdir(directory_path):
        print(get_Info_logging_string(f"'{directory_path}' is not a directory"))
        return 0
    
    # Get directory name from the path
    dir_name = os.path.basename(directory_path)
    files = sorted([f for f in os.listdir(directory_path) 
               if os.path.isfile(os.path.join(directory_path, f))])
    
    print(get_Info_logging_string(f"Processing directory '{dir_name}' with {len(files)} files"))
    
    renamed_count = 0

    if not files:
        return renamed_count
    
    for curr_num, filename in enumerate(files, 1):
        # Split filename and extension
        _, ext = os.path.splitext(filename)
        
        # Create new filename: directory_name-digits.extension
        new_filename = f"{dir_name}-{curr_num}{ext}"
        old_path = os.path.join(directory_path, filename)
        new_path = os.path.join(directory_path, new_filename)
        
        # Skip if new filename already exists
        if os.path.exists(new_path):
            print(get_Info_logging_string(f"Warning: Target file '{new_filename}' already exists. Skipping."))
            new_path += "(2)"
        
        # Rename file
        try:
            os.rename(old_path, new_path)
            print(get_Info_logging_string(f"Renamed: {filename} -> {new_filename}"))
            renamed_count += 1
        except Exception as e:
            print(get_Info_logging_string(f"Error renaming {filename}: {str(e)}"))
    
    return renamed_count


def process_root_directory(root_dir: str) -> tuple[int, int]:
    """
    Process all subdirectories in the root directory and rename files.
    
    Args:
        root_dir: Path to the root directory
        
    Returns:
        Tuple of (total_directories_processed, total_files_renamed)
    """
    print(get_Info_logging_string(f"Starting file renaming process in directory: {root_dir}"))
    
    # Get all subdirectories recursively
    subdirectories = get_all_subdirectories(root_dir)
    print(get_Info_logging_string(f"Found {len(subdirectories)} subdirectories to process"))
    
    total_renamed = 0
    
    for directory_path in subdirectories:
        renamed_count = rename_files_in_directory(directory_path)
        total_renamed += renamed_count
    
    return len(subdirectories), total_renamed


def main() -> None:
    """Main function to handle command line arguments and coordinate the renaming process."""
    parser = argparse.ArgumentParser(
        description="Rename files in subdirectories with pattern: subdir-number.extension"
    )
    parser.add_argument(
        "root_dir", 
        help="Root directory containing subdirectories with files"
    )
    
    args = parser.parse_args()
    
    # Validate root directory
    if not os.path.exists(args.root_dir):
        print(get_Info_logging_string(f"Error: Root directory '{args.root_dir}' does not exist"))
        return
    
    if not os.path.isdir(args.root_dir):
        print(get_Info_logging_string(f"Error: '{args.root_dir}' is not a directory"))
        return
    
    # Process all subdirectories
    directories_processed, files_renamed = process_root_directory(args.root_dir)
    
    print(get_Info_logging_string(
        f"Process completed. Processed {directories_processed} directories, "
        f"renamed {files_renamed} files total"
    ))


if __name__ == "__main__":
    main()
