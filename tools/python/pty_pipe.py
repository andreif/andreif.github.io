import json
import os
import select
import subprocess

UTF = 'utf-8', 'surrogatepass'


def read(fd, process):
    result = bytearray()
    while True:
        # Wait until file descriptor is ready for I/O
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            chunk = os.read(fd, 1024)
            if not chunk:  # EOF
                break
            result += chunk
        elif process.poll() is not None:  # Process ended
            break
    return result.decode(*UTF)


def pty_pipe(data, to):
    alpha, bravo = os.openpty()
    proc = subprocess.Popen(
        to, stdin=subprocess.PIPE, stdout=bravo, stderr=subprocess.PIPE, bufsize=0, text=False,
    )
    if isinstance(data, str):
        json_data = data
    else:
        json_data = json.dumps(data, ensure_ascii=False)
    proc.stdin.write(json_data.encode(*UTF))
    proc.stdin.close()
    if proc.returncode:
        raise Exception(proc.stderr.read().decode(*UTF).strip())
    result = read(alpha, proc).strip()
    proc.wait()
    os.close(alpha)
    os.close(bravo)
    return result
