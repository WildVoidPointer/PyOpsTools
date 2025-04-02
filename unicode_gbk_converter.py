from datetime import datetime
import sys
import os


def text_file_encoding_converter(
        text_file, origin_encode_type, target_encode_type, output_file=None):
    
    if not isinstance(text_file, str) or text_file == "" \
        or os.path.isfile(os.path.abspath(text_file)):

        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\
               - ERROR: The text file path parameter error")

    try:
        with open(text_file,"rb+") as text_file_obj:
            text = text_file_obj.read().decode(encoding=origin_encode_type)
            if output_file is not None:
                with open(output_file, "x", encoding=target_encode_type) as output_file:
                    output_file.write(text)
            else:
                text_file_obj.truncate(0)
                text_file_obj.seek(0)
                text_file_obj.write(text)
                
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\
               - INFO: The text file encoding is converted successfully")
    except (UnicodeDecodeError, UnicodeEncodeError):
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\
               - ERROR: The text file encoding conversion exception")
    except (FileExistsError, PermissionError):
        print(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\
               - ERROR: The text file cannot be accessed or read")


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python script.py <utf-8/gbk> <utf-8/gbk> <file_path>.")
        sys.exit(1)
    
    text_file_encoding_converter(sys.argv[4], sys.argv[2], sys.argv[3])
    print("Complete!")
