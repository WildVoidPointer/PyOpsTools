import os
import sys


def convert_lf_and_crlf(file_path, mode):
    try:
        with open(file_path, 'rb') as file:
            content = file.read()
        
        if mode:
            content = content.replace(b'\n', b'\r\n')
            
        else:
            content = content.replace(b'\r\n', b'\n')
        
        with open(file_path, 'wb') as file:
            file.write(content)
            print(f"Conversion completed: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def process_directory(directory, extensions, mode):
    """ Traverse a directory and convert files with specified extensions """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                convert_lf_and_crlf(file_path, mode)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_line_endings.py <directory> <extension1> <extension2> ...")
        sys.exit(1)

    target_directory = sys.argv[1]

    file_extensions = tuple(sys.argv[2:])

    if not os.path.isdir(target_directory):
        print(f"Error: Directory '{target_directory}' does not exist")
        sys.exit(1)

    process_directory(target_directory, file_extensions, False)
    print("Processing Complete!")
