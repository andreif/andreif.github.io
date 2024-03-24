import json
import subprocess
from pty_pipe import pty_pipe


def yq(value):
    subprocess.run(['yq', '-P'], input=json.dumps(value, ensure_ascii=False).encode())


def pty_yq(value):
    print(pty_pipe(data=value, to=['yq', '-P']))
