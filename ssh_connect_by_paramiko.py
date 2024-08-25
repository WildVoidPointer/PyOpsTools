from typing import Final
from paramiko import SSHClient, AutoAddPolicy, SSHException

class RemoteHostInformations:
    hostname: Final[str] = ''
    port: Final[int] = 22
    username: Final[str] = ''
    password: Final[str] = ''


def ssh_task_executor(hostname: str, port: int,
                      username: str, password: str, command: str) -> tuple[str, str] | None:
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        client.connect(hostname, port, username, password)
        stdin, stdout, stderr = client.exec_command(command)
        stdout.channel.recv_exit_status()
        stderr.channel.recv_exit_status()

        stdout_output = stdout.read().decode('utf-8').strip()
        stderr_output = stderr.read().decode('utf-8').strip()

        client.close()
        return stdout_output, stderr_output
    except SSHException as e:
        print("ERROR: ", e)
        return None
    

def ssh_task_exec_res_print(output_content: str) -> None:
    output_lines = output_content.splitlines() 
    print("\033[32m----- CONTENT START -----\033[0m")
    for line in output_lines:
        print(f"    {line}")  
    print("\33[32m----- CONTENT END -----\033[0m\n")



if __name__ == "__main__":
    task_command: str = 'ls'

    result: tuple[str, str] | None = ssh_task_executor(
        RemoteHostInformations.hostname, RemoteHostInformations.port,
        RemoteHostInformations.username, RemoteHostInformations.password,
        task_command
    )
    if isinstance(result, tuple) and len(result) == 2:
        ssh_task_exec_res_print(result[0])
        ssh_task_exec_res_print(result[1])
