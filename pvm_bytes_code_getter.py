from types import CodeType
import dis
import sys
import os


def get_pys_bytes_object(fname: str) -> CodeType:
    if not isinstance(fname, str) or fname == "" or \
        not os.path.isfile(fname):
        raise ValueError(f"The parameters is invalid in {__name__}")
    
    with open(fname, 'r', encoding='utf-8') as f:
        src = f.read()
        return compile(src, filename="<string>", mode="exec")


def print_pys_bytes_code(bytes_object) -> None:
    if bytes_object is None:
        raise ValueError(f"The parameters is invalid in {__name__}")

    dis.dis(bytes_object)


if __name__ == "__main__":
    b_object = get_pys_bytes_object(sys.argv[1])
    print_pys_bytes_code(b_object)
