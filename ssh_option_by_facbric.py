from fabric import Connection

# 连接到远程主机
conn = Connection(
    host='',
    user='',
    connect_kwargs={},
)

# 执行命令
result = conn.run('ls -l', hide=True)
print(result.stdout)