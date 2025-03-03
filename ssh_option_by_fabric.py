from fabric import Connection

# 连接到远程主机
conn = Connection(
    host='',
    user='',
    connect_kwargs={},
)
command = "ls -l"
# 执行命令
result = conn.run(command, hide=True)
print(result.stdout)