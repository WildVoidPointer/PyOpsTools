from datetime import datetime
import sys
import os


def convert_text_file_encoding(
        text_file, origin_encode_type, target_encode_type, output_file=None):
    
    if not isinstance(text_file, str) or text_file == "" or \
        not os.path.isfile(os.path.abspath(text_file)):
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: The text file path parameter error"
        )
        return

    try:
        with open(text_file, "rb+") as text_file_obj:
            text = text_file_obj.read().decode(encoding=origin_encode_type)
            if output_file is not None:
                with open(output_file, "x", encoding=target_encode_type) as output_file_obj:
                    output_file_obj.write(text)
            else:
                text_file_obj.truncate(0)
                text_file_obj.seek(0)
                text_file_obj.write(text.encode(target_encode_type))
                
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - INFO: {text_file} converted successfully"
        )
    except (UnicodeDecodeError, UnicodeEncodeError):
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: Encoding conversion error in {text_file}"
        )
    except (FileExistsError, PermissionError):
        print(
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: Cannot access or write to {text_file}"
        )


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage:  python script.py -f/-d <from_encoding> <to_encoding> <file_path>")
        sys.exit(1)

    mode = sys.argv[1]
    from_enc = sys.argv[2]
    to_enc = sys.argv[3]
    path = sys.argv[4]

    if mode == "-f":
        convert_text_file_encoding(path, from_enc, to_enc)
    elif mode == "-d":
        if not os.path.isdir(path):
            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: Directory not found")
            sys.exit(1)
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                convert_text_file_encoding(file_path, from_enc, to_enc)
    else:
        print("Invalid mode. Use -f for file or -d for directory.")
        sys.exit(1)

    print("Complete!")
