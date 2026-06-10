import sys
import os


def replace_latex_delimiters(file_path):
    r"""
    Read the content of the specified file, perform LaTeX math delimiter replacements,
    then write the modified content back to the original file.

    Replacement rules:
    - \[ replaced with $$
    - \] replaced with $$
    - \( replaced with $
    - \) replaced with $
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing file: {file_path}")

    try:
        # 1. Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 2. Perform replacements
        # Note: In Python strings, backslash '\' is an escape character.
        # To match literal '\[', we need to write '\\[' in the Python string,
        # so it becomes '\[' in memory.
        # To match \(, write '\\('.

        # Replace \[ with $$ and \] with $$
        content = content.replace(r'\[', '$$')
        content = content.replace(r'\]', '$$')

        # Replace \( with $ and \) with $
        content = content.replace(r'\(', '$')
        content = content.replace(r'\)', '$')

        # 3. Write modified content back to the original file (in-place modification)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("Replacement completed.")

    except Exception as e:
        print(f"Error occurred while processing file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Check if a filename argument is provided
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename>", file=sys.stderr)
        print(f"  Example: {sys.argv[0]} my_text_file.txt", file=sys.stderr)
        sys.exit(1)

    file_name = sys.argv[1]
    replace_latex_delimiters(file_name)
    