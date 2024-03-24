#!/usr/bin/env python
import json
import os
import re
import subprocess
import sys


def parse(path):
    p = subprocess.run(['defaults', 'read', os.path.abspath(path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise NotImplementedError(p.stderr.decode())
    o = p.stdout.decode()
    o = re.sub(r' = ([^"]+);\n', ' = "\\1",\n', o)
    o = re.sub(r'(\S+) =\s*', '"\\1": ', o)
    o = re.sub(r':\s+\(', ': [', o)
    o = re.sub(r';\n', ',\n', o)
    o = re.sub(r'\)(,?)\n', ']\\1\n', o)
    o = re.sub(r',(\s+[}\]])', '\\1', o)
    return json.loads(o)


if __name__ == '__main__':
    print(json.dumps(parse(sys.argv[1])))
