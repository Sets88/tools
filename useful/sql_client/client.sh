export CLHOST="hostname"
export CLUSER="username"
export CLPASS='encrypted with ssh_crypt pass'
export CLENGINE="clickhouse"
./.venv/bin/python client.py somefile.sql
