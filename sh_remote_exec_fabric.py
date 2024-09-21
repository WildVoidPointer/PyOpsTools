from fabric import Connection


script_path = ""
script_content = None


with open(script_path, 'r') as script_f:
    script_content = script_f.read()


conn = Connection(
    host='',
    user='',
    connect_kwargs={},
)

exec_result = conn.run(script_content, hide=True)
print(exec_result.stderr)
print(exec_result.stdout)
