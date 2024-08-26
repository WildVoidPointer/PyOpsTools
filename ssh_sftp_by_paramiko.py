from typing import Final
from paramiko import SSHClient, AutoAddPolicy, SSHException

class RemoteHostInformations:
    hostname: Final[str] = ''
    port: Final[int] = 22
    username: Final[str] = ''
    password: Final[str] = ''


def ssh_sftp_executor(hostname: str, port: int, username: str, password: str, 
                      local_file: str, remote_file: str, download_flag: bool = False) -> bool:
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        client.connect(hostname, port, username, password)  # Connect to the ssh client
        sftp = client.open_sftp()
        if not download_flag:
            sftp.put(local_file, remote_file)   # upload file
        else:
            sftp.get(remote_file, local_file)   # download file

        sftp.close()
        return True
    except SSHException as e:
        print("ERROR: ", e)
        return False
    

def ssh_task_exec_res_print(output_content: str) -> None:
    output_lines = output_content.splitlines() 
    print("\033[32m----- CONTENT START -----\033[0m")
    for line in output_lines:
        print(f"    {line}")  
    print("\033[32m----- CONTENT END -----\033[0m\n")



if __name__ == "__main__":
    local_path: str = './filename_to_hashcode.py'
    remote_path: str = '/home/dev/n_to_hash.py'

    result_status: bool = ssh_sftp_executor(
        RemoteHostInformations.hostname, RemoteHostInformations.port,
        RemoteHostInformations.username, RemoteHostInformations.password,
        local_path, remote_path
    )

    print(f"\033[32m{str(result_status)}\33[0m")
