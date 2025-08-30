from datetime import datetime
from typing import Optional
import argparse
import shutil
import sys
import os


def get_Info_logging_string(content: str) -> str:
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - RUNTIME_INFO - {content}"


def copy_directory_contents(source_dir: str, target_dir: Optional[str] = None) -> Optional[str]:
    """
    Copy all contents from source directory to target directory.
    If target_dir is not provided, copy to parent directory with name 'source_dirBak'
    """
    if not os.path.exists(source_dir):
        print(get_Info_logging_string(f"Source directory '{source_dir}' does not exist"))
        return None
    
    if target_dir is None:
        parent_dir: str = os.path.dirname(source_dir)
        dir_name: str = os.path.basename(source_dir)
        target_dir = os.path.join(parent_dir, f"{dir_name}Bak")
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    try:
        # Copy all contents from source to target
        for item in os.listdir(source_dir):
            source_item: str = os.path.join(source_dir, item)
            target_item: str = os.path.join(target_dir, item)
            
            if os.path.isdir(source_item):
                shutil.copytree(source_item, target_item, dirs_exist_ok=True)
            else:
                shutil.copy2(source_item, target_item)
        
        print(get_Info_logging_string(f"Successfully copied contents from '{source_dir}' to '{target_dir}'"))
        return target_dir
    except Exception as e:
        print(get_Info_logging_string(f"Error copying directory: {e}"))
        return None


def flatten_directory(directory: str) -> bool:
    """
    Move all files from subdirectories to the root directory and remove empty subdirectories
    """
    if not os.path.exists(directory):
        print(get_Info_logging_string(f"Directory '{directory}' does not exist"))
        return False
    
    try:
        # Walk through all subdirectories and move files to root
        for root, dirs, files in os.walk(directory, topdown=False):
            if root == directory:
                continue  # Skip the root directory itself
                
            for file in files:
                source_file: str = os.path.join(root, file)
                target_file: str = os.path.join(directory, file)
                
                # Handle filename conflicts
                counter: int = 1
                base_target_file: str = target_file
                while os.path.exists(target_file):
                    name, ext = os.path.splitext(file)
                    target_file = os.path.join(directory, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.move(source_file, target_file)
                print(get_Info_logging_string(f"Moved '{source_file}' to '{target_file}'"))
        
        # Remove empty subdirectories
        for root, dirs, files in os.walk(directory, topdown=False):
            if root == directory:
                continue  # Skip the root directory itself
                
            try:
                if not os.listdir(root):  # Check if directory is empty
                    os.rmdir(root)
                    print(get_Info_logging_string(f"Removed empty directory: '{root}'"))
            except OSError as e:
                print(get_Info_logging_string(f"Error removing directory '{root}': {e}"))
        
        print(get_Info_logging_string(f"Successfully flattened directory '{directory}'"))
        return True
    except Exception as e:
        print(get_Info_logging_string(f"Error flattening directory: {e}"))
        return False


def validate_directory(path: str) -> bool:
    """Validate if the given path exists and is a directory"""
    if not os.path.exists(path):
        print(get_Info_logging_string(f"Path '{path}' does not exist"))
        return False
    if not os.path.isdir(path):
        print(get_Info_logging_string(f"Path '{path}' is not a directory"))
        return False
    return True


def parse_arguments() -> tuple[str, Optional[str]]:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Copy and flatten directory contents")
    parser.add_argument("source_dir", help="Source directory to process")
    parser.add_argument("target_dir", nargs="?", help="Target directory for backup (optional)")
    
    args: argparse.Namespace = parser.parse_args()
    
    return args.source_dir, args.target_dir


def main() -> None:
    """Main function to execute the script"""
    # Parse command line arguments
    source_dir: str
    target_dir: Optional[str]
    source_dir, target_dir = parse_arguments()
    
    # Validate source directory
    if not validate_directory(source_dir):
        sys.exit(1)
    
    # Step 1: Copy directory contents
    print(get_Info_logging_string("Starting backup process..."))
    backup_path: Optional[str] = copy_directory_contents(source_dir, target_dir)
    
    if backup_path is None:
        print(get_Info_logging_string("Backup failed. Exiting."))
        sys.exit(1)
    
    # Step 2: Flatten the source directory
    print(get_Info_logging_string("Starting flattening process..."))
    success: bool = flatten_directory(source_dir)
    
    if not success:
        print(get_Info_logging_string("Flattening process failed"))
    
    # Step 3: Output backup path
    print(get_Info_logging_string(f"Backup created at: {backup_path}"))


if __name__ == "__main__":
    main()
