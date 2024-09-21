from fabric import Connection


conn = Connection(
    host='',
    user='',
    connect_kwargs={},
)
command = "ls -l"

result = conn.run(command, hide=True)
print(result.stdout)