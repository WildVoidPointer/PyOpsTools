#!/usr/bin/env python3
"""
AppleDesktop Files Collector
Recursively collects ._* and .DS_Store files and moves them to a target directory.
Each file is prefixed with "ADF". If a conflict occurs, numbering is used:
"ADF(1)original_name", "ADF(2)original_name", ...
"""

from typing import Optional, Final
from enum import IntEnum, StrEnum
from datetime import datetime
from pathlib import Path
import argparse
import shutil
import sys
import os


class ADFCollectorUtils:
    class LoggingLevel(StrEnum):
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"

    @staticmethod
    def logging_println(level: LoggingLevel, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - [{level}] - {message}")


class ADFCollectorExitCode(IntEnum):
    SUCCESS = 0
    INVALID_DIRECTORY = 1
    MOVE_FAILED = 2
    USAGE_ERROR = 3
    UNKNOWN_ERROR = 4


class AppleDesktopFilesCollector:

    PREFIX: Final[str] = "ADF"

    def __init__(self, src: Path, dest: Optional[Path] = None) -> None:
        self.src = src.resolve()
        self.dest = dest.resolve() if dest else None
        self.files: list[Path] = []          # 捕获到的 AppleDesktop 文件列表
        self.dest_dir: Optional[Path] = None  # 实际使用的目标目录（移动时确定）

    def dir_is_access(self, path: Path) -> bool:
        return (
            path.exists() and path.is_dir()
            and os.access(str(path), os.X_OK | os.R_OK | os.W_OK)
        )

    def is_desktop_file(self, filename: str) -> bool:
        return filename.startswith("._") or filename == ".DS_Store"

    def capture(self) -> None:
        """收集源目录下所有 AppleDesktop 文件，存入 self.files"""
        if not self.dir_is_access(self.src):
            ADFCollectorUtils.logging_println(
                ADFCollectorUtils.LoggingLevel.ERROR,
                "The specified directory does not exist or is inaccessible"
            )
            sys.exit(ADFCollectorExitCode.INVALID_DIRECTORY)

        found_files: list[Path] = []
        for entry in self.src.rglob("*"):
            if entry.is_file() and self.is_desktop_file(entry.name):
                found_files.append(entry)

        self.files = found_files

    def _prepare_dest_dir(self) -> None:
        """根据 self.dest 准备实际的目标目录，存入 self.dest_dir"""
        if self.dest is None:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            dir_name = f"AppleDesktopFiles{timestamp}"
            self.dest_dir = self.src / dir_name
        else:
            self.dest_dir = self.dest

        # 确保目标目录存在
        try:
            self.dest_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            ADFCollectorUtils.logging_println(
                ADFCollectorUtils.LoggingLevel.ERROR,
                f"Cannot create target directory '{self.dest_dir}': {e}"
            )
            sys.exit(ADFCollectorExitCode.MOVE_FAILED)

    def _get_unique_name(self, filename: str) -> Path:
        """
        生成目标目录下唯一的文件路径。
        每个文件都加上前缀 'ADF'，如果冲突则使用 'ADF(1)'、'ADF(2)' 等编号。
        """
        if self.dest_dir is None:
            ADFCollectorUtils.logging_println(
                ADFCollectorUtils.LoggingLevel.ERROR,
                "Destination directory is not set"
            )
            sys.exit(ADFCollectorExitCode.INVALID_DIRECTORY)

        base_name = f"{self.PREFIX}{filename}"
        candidate = self.dest_dir / base_name

        if not candidate.exists():
            return candidate

        counter = 1
        while True:
            new_name = f"{self.PREFIX}({counter}){filename}"
            candidate = self.dest_dir / new_name
            if not candidate.exists():
                return candidate
            counter += 1

    def move(self) -> None:
        """
        将 self.files 中的 AppleDesktop 文件移动到 self.dest_dir。
        无统计输出，仅执行移动操作。
        """
        if not self.dir_is_access(self.src) or not self.files:
            ADFCollectorUtils.logging_println(
                ADFCollectorUtils.LoggingLevel.ERROR,
                "Invalid root path or no files to move"
            )
            sys.exit(ADFCollectorExitCode.MOVE_FAILED)

        self._prepare_dest_dir()

        moved_count: int = 0

        for src_path in self.files:
            dest_path = self._get_unique_name(src_path.name)
            try:
                shutil.move(str(src_path), str(dest_path))
                ADFCollectorUtils.logging_println(
                    ADFCollectorUtils.LoggingLevel.INFO,
                    f"Moved: {src_path} -> {dest_path}"
                )
                moved_count += 1
            except Exception as e:
                ADFCollectorUtils.logging_println(
                    ADFCollectorUtils.LoggingLevel.ERROR,
                    f"Failed to move {src_path}: {e}"
                )
        ADFCollectorUtils.logging_println(
            ADFCollectorUtils.LoggingLevel.INFO,
            f"Total files moved: {moved_count}"
        )

    def collect(self) -> None:
        """整理流程"""
        self.capture()
        if not self.files:
            ADFCollectorUtils.logging_println(
                ADFCollectorUtils.LoggingLevel.INFO,
                "No AppleDesktop files found."
            )
            return

        self.move()


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively collect AppleDesktop files (._* and .DS_Store) "
            "and move them to a target directory. Each file gets prefix 'ADF'."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Root directory to scan for AppleDesktop files"
    )
    parser.add_argument(
        "-t", "--target",
        dest="target_dir",
        type=Path,
        default=None,
        help="Target directory to move files into. If not provided, "
             "a timestamped subdirectory will be created under the source directory."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if not args.directory.exists() or not args.directory.is_dir():
        ADFCollectorUtils.logging_println(
            ADFCollectorUtils.LoggingLevel.ERROR,
            f"Source directory does not exist or is not a directory: {args.directory}"
        )
        sys.exit(ADFCollectorExitCode.INVALID_DIRECTORY)

    try:
        organizer = AppleDesktopFilesCollector(args.directory, args.target_dir)
        organizer.collect()
    except KeyboardInterrupt:
        ADFCollectorUtils.logging_println(
            ADFCollectorUtils.LoggingLevel.WARNING,
            "Interrupted by user"
        )
        sys.exit(ADFCollectorExitCode.UNKNOWN_ERROR)
    except Exception as e:
        ADFCollectorUtils.logging_println(
            ADFCollectorUtils.LoggingLevel.ERROR,
            f"Unexpected error: {e}"
        )
        sys.exit(ADFCollectorExitCode.UNKNOWN_ERROR)

    sys.exit(ADFCollectorExitCode.SUCCESS)


if __name__ == "__main__":
    main()
