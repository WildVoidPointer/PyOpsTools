#!/usr/bin/env python3
"""Filename Obfuscator
Recursively obfuscates file names in a specified directory by renaming them to 
their hash values (with original extensions preserved).
The hash is generated based on the original filename and a random salt
"""

from enum import StrEnum, IntEnum
from datetime import datetime
from typing import Optional
from pathlib import Path
import argparse
import hashlib
import secrets
import time
import sys


class FilenameObfuscatorUtils:
    class LoggingLevel(StrEnum):
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"

    @staticmethod
    def logging_println(level: LoggingLevel, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - [{level}] - {message}")


class ObfuscatorExitCode(IntEnum):
    """程序退出码"""
    SUCCESS = 0
    INVALID_DIRECTORY = 1
    PARTIAL_FAILURE = 2
    NO_FILES_PROCESSED = 3


class FilenamesObfuscator:
    """批量重命名文件为哈希值（基于文件名+随机盐）的执行器"""

    def __init__(self, root: Path, ignore_hidden: bool = False):
        """
        初始化重命名器

        Args:
            root: 要处理的根目录（Path 对象）
            ignore_hidden: 是否忽略隐藏文件（文件名以点开头）
        """
        self.root = root.resolve()
        self.ignore_hidden = ignore_hidden
        self.files: list[Path] = []

    def _get_random_salt(self) -> str:
        """生成16字节随机盐（十六进制字符串）"""
        return secrets.token_hex(16)

    def _generate_hashcode(
        self, filename: str, salt: str, hash_type: str = 'sha1'
    ) -> Optional[str]:
        """
        仅依据文件名和随机盐生成哈希值（不再抛出异常）

        Args:
            filename: 原始文件名（含扩展名）
            salt: 随机盐字符串
            hash_type: 哈希算法（默认 sha1）

        Returns:
            成功返回哈希值的十六进制字符串，失败返回 None
        """
        if not filename or not salt:
            FilenameObfuscatorUtils.logging_println(
                FilenameObfuscatorUtils.LoggingLevel.ERROR,
                "Filename and salt must be non-empty strings "
                f"(filename='{filename}', salt='{salt}')"
            )
            return None

        content = filename + salt
        try:
            hasher = hashlib.new(hash_type)
            hasher.update(content.encode('utf-8'))
            return hasher.hexdigest().lower()
        except ValueError:
            FilenameObfuscatorUtils.logging_println(
                FilenameObfuscatorUtils.LoggingLevel.ERROR,
                f"Unsupported hash type: {hash_type}"
            )
            return None

    def _rename_file(self, file_path: Path, hashcode: str) -> bool:
        """
        将文件重命名为哈希值 + 原扩展名

        Args:
            file_path: 原始文件 Path 对象
            hashcode: 哈希值字符串

        Returns:
            重命名成功返回 True，否则 False
        """
        parent = file_path.parent
        ext = file_path.suffix
        new_name = hashcode + ext
        new_path = parent / new_name

        if new_path.exists():
            FilenameObfuscatorUtils.logging_println(
                FilenameObfuscatorUtils.LoggingLevel.WARNING,
                f"Target file already exists, skip rename: {new_path}"
            )
            return False

        try:
            file_path.rename(new_path)
            return True
        except OSError as e:
            FilenameObfuscatorUtils.logging_println(
                FilenameObfuscatorUtils.LoggingLevel.ERROR,
                f"Rename failed for {file_path}: {e}"
            )
            return False

    def scan_files(self) -> None:
        """
        扫描根目录下所有文件，并根据 ignore_hidden 过滤隐藏文件。
        结果存储在 self.files 列表中。
        """
        self.files.clear()
        for item in self.root.rglob('*'):
            if item.is_file():
                if self.ignore_hidden and item.name.startswith('.'):
                    continue
                self.files.append(item)

        FilenameObfuscatorUtils.logging_println(
            FilenameObfuscatorUtils.LoggingLevel.INFO,
            f"Scanned {len(self.files)} files (ignored hidden: {self.ignore_hidden})"
        )

    def execute_rename(self) -> tuple[int, int, list[Path]]:
        """
        执行批量重命名操作

        Returns:
            元组 (总文件数, 成功数, 失败文件列表)
        """
        if not self.files:
            FilenameObfuscatorUtils.logging_println(
                FilenameObfuscatorUtils.LoggingLevel.WARNING,
                "No files to process."
            )
            return 0, 0, []

        success_count = 0
        failure_files: list[Path] = []

        for file_path in self.files:
            salt = self._get_random_salt()
            hashcode = self._generate_hashcode(file_path.name, salt)
            if hashcode is None:
                FilenameObfuscatorUtils.logging_println(
                    FilenameObfuscatorUtils.LoggingLevel.ERROR,
                    f"Hash generation failed for {file_path.name}"
                )
                failure_files.append(file_path)
                continue

            if self._rename_file(file_path, hashcode):
                success_count += 1
            else:
                failure_files.append(file_path)

        return len(self.files), success_count, failure_files


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Batch rename files to hash values "
        "based on original filename and random salt."
    )
    parser.add_argument("directory", type=str, help="Root directory to process")
    parser.add_argument(
        "--ignore-hidden", 
        action="store_true",
        help="Ignore hidden files (those whose name starts with a dot)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    root = Path(args.directory)
    if not root.is_dir():
        FilenameObfuscatorUtils.logging_println(
            FilenameObfuscatorUtils.LoggingLevel.ERROR,
            f"Provided path is not a valid directory: {args.directory}"
        )
        sys.exit(ObfuscatorExitCode.INVALID_DIRECTORY)

    start_time = time.time()

    obfuscator = FilenamesObfuscator(root=root, ignore_hidden=args.ignore_hidden)
    obfuscator.scan_files()
    total, success, failures = obfuscator.execute_rename()

    # 输出统计信息
    FilenameObfuscatorUtils.logging_println(
        FilenameObfuscatorUtils.LoggingLevel.INFO,
        f"Total files scanned: {total}"
    )
    FilenameObfuscatorUtils.logging_println(
        FilenameObfuscatorUtils.LoggingLevel.INFO,
        f"Successful renames: {success}, Failed: {len(failures)}"
    )
    if failures:
        FilenameObfuscatorUtils.logging_println(
            FilenameObfuscatorUtils.LoggingLevel.WARNING,
            "Failed files:"
        )
        for f in failures:
            FilenameObfuscatorUtils.logging_println(
                FilenameObfuscatorUtils.LoggingLevel.WARNING,
                f"  {f}"
            )

    elapsed = time.time() - start_time
    FilenameObfuscatorUtils.logging_println(
        FilenameObfuscatorUtils.LoggingLevel.INFO,
        f"Running time: {elapsed:.3f}s"
    )
    FilenameObfuscatorUtils.logging_println(
        FilenameObfuscatorUtils.LoggingLevel.INFO,
        "Complete!"
    )

    if total == 0:
        sys.exit(ObfuscatorExitCode.NO_FILES_PROCESSED)
    elif len(failures) > 0:
        sys.exit(ObfuscatorExitCode.PARTIAL_FAILURE)
    else:
        sys.exit(ObfuscatorExitCode.SUCCESS)


if __name__ == "__main__":
    main()
