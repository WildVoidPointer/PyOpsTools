#!/usr/bin/env python3
"""
SSH 密钥规范结构初始化工具
"""
from enum import StrEnum, IntEnum
from datetime import datetime
from typing import Optional
from pathlib import Path
import subprocess
import argparse
import shutil
import sys


class SSHKeygenExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    SSH_DIR_NOT_INITIALIZED = 2
    OPERATION_CANCELLED = 3


class SSHKeyType(StrEnum):
    ED25519 = "ed25519"
    RSA = "rsa"
    ECDSA = "ecdsa"


class SSHKeygenConfigInitializerUtils:
    class LoggingLevel(StrEnum):
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"

    @staticmethod
    def logging_println(level: LoggingLevel, message: str):
        """统一日志输出格式"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - [{level}] - {message}")


class SSHKeygenConfigInitializer:
    def __init__(self, args: argparse.Namespace) -> None:
        """接收已解析的命令行参数"""
        self.args = args
        self.ssh_dir: Optional[Path] = None
        self.name: Optional[str] = None
        self.domain: Optional[str] = None
        self.key_type: Optional[SSHKeyType] = None
        self.key_bits: Optional[int] = None
        self.private_key_path: Optional[Path] = None

    def ensure_ssh_dir(self) -> Path:
        """确保 ~/.ssh 目录存在并返回其 Path 对象"""
        ssh_dir = Path.home() / ".ssh"
        if ssh_dir.exists() and not ssh_dir.is_dir():
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.ERROR,
                f"{ssh_dir} exists but is not a directory. Please resolve this issue."
            )
            sys.exit(SSHKeygenExitCode.GENERAL_ERROR)

        ssh_dir.mkdir(mode=0o700, exist_ok=True)
        self.ssh_dir = ssh_dir
        return ssh_dir

    def interactive_key_choice(self) -> tuple[SSHKeyType, Optional[int]]:
        """交互式收集密钥类型和位数，返回 (key_type, key_bits)"""
        print("\nSSH Keygen Config Initializer - Interactive Mode (Key Selection)")

        SSHKeygenConfigInitializerUtils.logging_println(
            SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
            f"Using name: {self.name}, domain: {self.domain} (from command line)"
        )

        print("\nSelect key type:")
        print("  1. ed25519 (recommended, most secure and fast)")
        print("  2. rsa")
        print("  3. ecdsa")
        choice = input("Enter number (1-3, default 1): ").strip() or "1"

        key_type_map: dict[str, SSHKeyType] = {
            "1": SSHKeyType.ED25519,
            "2": SSHKeyType.RSA,
            "3": SSHKeyType.ECDSA,
        }
        key_type = key_type_map.get(choice, SSHKeyType.ED25519)

        SSHKeygenConfigInitializerUtils.logging_println(
            SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
            f"Selected key type: {key_type}"
        )

        key_bits: Optional[int] = None

        if key_type == SSHKeyType.RSA:
            print("\nSelect RSA key length:")
            print("  1. 2048 (best compatibility)")
            print("  2. 3072 (balanced)")
            print("  3. 4096 (recommended, high security)")
            rsa_choice = input("Enter number (1-3, default 3): ").strip() or "3"
            bits_map = {"1": 2048, "2": 3072, "3": 4096}
            key_bits = bits_map.get(rsa_choice, 4096)
        elif key_type == SSHKeyType.ECDSA:
            print("\nSelect ECDSA key length:")
            print("  1. 256 (good compatibility)")
            print("  2. 384")
            print("  3. 521 (recommended, highest security)")
            ecdsa_choice = input("Enter number (1-3, default 3): ").strip() or "3"
            bits_map = {"1": 256, "2": 384, "3": 521}
            key_bits = bits_map.get(ecdsa_choice, 521)

        SSHKeygenConfigInitializerUtils.logging_println(
            SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
            f"Selected {key_type} key bits: {key_bits or 'default'}"
        )
        return key_type, key_bits

    def generate_keypair(self, name: str, key_type: SSHKeyType, key_bits: Optional[int]) -> Path:
        """
        调用 ssh-keygen 生成密钥对，返回私钥路径。
        公钥位于同一目录下，扩展名为 .pub。
        """
        if self.ssh_dir is None:
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.ERROR,
                "SSH directory not initialized. Call ensure_ssh_dir() first."
            )
            sys.exit(SSHKeygenExitCode.SSH_DIR_NOT_INITIALIZED)

        key_dir = self.ssh_dir / name
        key_dir.mkdir(mode=0o700, exist_ok=True)
        private_key_path = key_dir / name
        public_key_path = private_key_path.with_suffix(".pub")

        if private_key_path.exists():
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.WARNING,
                f"Key {private_key_path} already exists."
            )
            allow_overwrite = input(
                f"Key {private_key_path} already exists, overwrite? (y/N): "
            ).strip().lower()
            if allow_overwrite != "y":
                SSHKeygenConfigInitializerUtils.logging_println(
                    SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
                    "Operation cancelled."
                )
                sys.exit(SSHKeygenExitCode.OPERATION_CANCELLED)

        cmd = ["ssh-keygen", "-t", key_type, "-f", str(private_key_path), "-N", ""]
        if key_type in (SSHKeyType.RSA, SSHKeyType.ECDSA) and key_bits is not None:
            cmd.extend(["-b", str(key_bits)])

        try:
            subprocess.run(
                cmd,
                check=True,
            )
        except FileNotFoundError:
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.ERROR,
                "ssh-keygen command not found. Please ensure it is installed and in your PATH."
            )
            sys.exit(SSHKeygenExitCode.GENERAL_ERROR)
        except subprocess.CalledProcessError as e:
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.ERROR,
                f"Key generation failed: {e.stderr.decode()}"
            )
            sys.exit(SSHKeygenExitCode.GENERAL_ERROR)

        SSHKeygenConfigInitializerUtils.logging_println(
            SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
            f"Key generated ({key_type}, {key_bits or 'default'} bits):\n  "
            f"Private: {private_key_path}\n  Public: {public_key_path}"
        )
        return private_key_path

    def update_ssh_config(self, name: str, domain: str, private_key_path: Path) -> None:
        """
        向 ~/.ssh/config 添加或更新主机配置条目。
        操作前自动备份原 config 文件为 config.backup。
        如果发现同名 Host 条目，则输出警告日志，
        交互模式下询问用户是否替换，非交互模式下直接替换。
        """
        config_path = Path.home() / ".ssh" / "config"
        new_block = (
            f"Host {name}\n"
            f"    HostName {domain}\n"
            f"    PreferredAuthentications publickey\n"
            f"    IdentityFile {private_key_path}\n"
        )

        # 如果 config 文件不存在，直接创建并写入
        if not config_path.exists():
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
                f"Config file {config_path} does not exist. Creating new one."
            )

            config_path.write_text(new_block)
            config_path.chmod(0o600)

            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
                f"Created config file and added host {name}"
            )
            return

        # 读取现有配置行
        lines = config_path.read_text().splitlines()

        # 检查是否已存在同名 Host 条目
        host_exists = False
        i = 0
        while i < len(lines):
            stripped = lines[i].strip()
            if stripped.startswith("Host "):
                parts = stripped.split(maxsplit=1)
                if len(parts) == 2 and parts[1] == name:
                    host_exists = True
                    break
            i += 1

        # 如果存在同名条目，处理重复
        if host_exists:
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.WARNING,
                f"Host '{name}' already exists in config file."
            )

            replace = False
            if self.args.non_interactive:
                replace = True
            else:
                response = input(
                    f"Replace existing configuration for host '{name}'? (y/N): "
                ).strip().lower()
                replace = (response == 'y')

            if not replace:
                SSHKeygenConfigInitializerUtils.logging_println(
                    SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
                    f"Skipped updating config for host '{name}'."
                    " You may need to manually add it."
                )
                return

        # 备份 config 文件
        backup_path = config_path.with_suffix(".backup")
        shutil.copy2(config_path, backup_path)
        SSHKeygenConfigInitializerUtils.logging_println(
            SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
            f"Backed up existing config to {backup_path}"
        )

        # 执行替换或追加操作
        updated_lines = []
        i = 0
        replaced = False

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            # 检查是否是 Host 行且匹配目标名称
            if stripped.startswith("Host "):
                parts = stripped.split(maxsplit=1)
                if len(parts) == 2 and parts[1] == name:
                    # 跳过当前整个 Host 块（包括其内部缩进行）
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith("Host "):
                        i += 1
                    # 插入新配置块
                    updated_lines.append(new_block.rstrip('\n'))
                    replaced = True
                    continue
            updated_lines.append(line)
            i += 1

        if not replaced:
            if updated_lines and updated_lines[-1] != "":
                updated_lines.append("")
            updated_lines.append(new_block.rstrip('\n'))
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
                f"Appended host {name} to config file"
            )
        else:
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
                f"Replaced host {name} configuration"
            )

        # 写回修改后的内容并设置权限
        config_path.write_text("\n".join(updated_lines))
        config_path.chmod(0o600)

    def print_keys_info(self, private_key_path: Path) -> None:
        """打印私钥路径、公钥路径、公钥内容与 git 初始化建议"""
        public_key_path = private_key_path.with_suffix(".pub")
        try:
            public_key_content = public_key_path.read_text().strip()
        except Exception as e:
            public_key_content = f"<Failed to read public key: {e}>"

        print(
            f"Key information:\n"
            f"  Private key path: {private_key_path}\n"
            f"  Public key path: {public_key_path}\n"
            f"  Public key content: {public_key_content}\n"
            "  Git initialization suggestion: "
            f"git remote add origin git@{self.name}: <repository-name>"
        )

    def run(self) -> None:
        """主流程：根据模式收集参数，生成密钥，更新配置"""
        self.name = self.args.name
        self.domain = self.args.domain

        if self.args.non_interactive:
            key_type_str = self.args.key_type
            if key_type_str == "ed25519":
                key_type = SSHKeyType.ED25519
            elif key_type_str == "rsa":
                key_type = SSHKeyType.RSA
            else:  # ecdsa
                key_type = SSHKeyType.ECDSA

            key_bits = self.args.key_bits

            if key_type in (SSHKeyType.RSA, SSHKeyType.ECDSA) and key_bits is None:
                SSHKeygenConfigInitializerUtils.logging_println(
                    SSHKeygenConfigInitializerUtils.LoggingLevel.WARNING,
                    f"--key-bits not specified, using default (RSA:4096, ECDSA:521)"
                )
                if key_type == SSHKeyType.RSA:
                    key_bits = 4096
                else:
                    key_bits = 521
            elif key_type == SSHKeyType.ED25519 and key_bits is not None:
                SSHKeygenConfigInitializerUtils.logging_println(
                    SSHKeygenConfigInitializerUtils.LoggingLevel.WARNING,
                    "ed25519 does not need --key-bits, ignoring it."
                )
                key_bits = None
        else:
            key_type, key_bits = self.interactive_key_choice()

        if not self.name or not self.domain:
            SSHKeygenConfigInitializerUtils.logging_println(
                SSHKeygenConfigInitializerUtils.LoggingLevel.ERROR,
                "Name and domain must be provided (either via command line or interactive mode)."
            )
            sys.exit(SSHKeygenExitCode.GENERAL_ERROR)

        self.ensure_ssh_dir()
        private_key = self.generate_keypair(self.name, key_type, key_bits)
        self.update_ssh_config(self.name, self.domain, private_key)
        self.print_keys_info(private_key)

        SSHKeygenConfigInitializerUtils.logging_println(
            SSHKeygenConfigInitializerUtils.LoggingLevel.INFO,
            "Initialization completed."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="初始化 SSH 服务密钥并更新 config (默认交互模式)"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="使用非交互模式 (需提供 name 和 domain 位置参数)"
    )
    parser.add_argument(
        "--name",
        nargs="?",
        required=True,
        help="密钥名称"
    )
    parser.add_argument(
        "--domain",
        nargs="?",
        required=True,
        help="目标服务器域名或地址"
    )
    parser.add_argument(
        "--key-type",
        choices=["ed25519", "rsa", "ecdsa"],
        default="ed25519",
        help="非交互模式下使用的密钥类型 (默认 ed25519)"
    )
    parser.add_argument(
        "--key-bits",
        type=int,
        help="非交互模式下 RSA/ECDSA 的密钥长度"
    )

    args = parser.parse_args()

    app = SSHKeygenConfigInitializer(args)
    app.run()
    sys.exit(SSHKeygenExitCode.SUCCESS)


if __name__ == "__main__":
    main()
