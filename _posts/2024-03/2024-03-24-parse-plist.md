---
title: Parsing property lists (*.plist) with Python
category: Tools
tags: macos cli python
---

Sometimes one needs to know state of a plist before changing settings. For example, 
when changing [LSHandlers in LaunchServices](/claimed-utis).

We can see what's inside the file using `defaults read` command:

```shell
$ defaults read ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist
{
    LSHandlers =     (
                {
            LSHandlerPreferredVersions =             {
                LSHandlerRoleAll = "-";
            };
            LSHandlerRoleAll = "us.zoom.xos";
            LSHandlerURLScheme = zoomphonecall;
        },
...
```

Now we could use [`plists`](https://pypi.org/project/plists/), pure-python stdlib-only Python 
package to parse the binary plist file, but the output of `defaults` looks so close to JSON 
that we could just convert it with just a few changes.

Let's make `plist.py` containing:

```python
#!/usr/bin/env python
import json
import os
import re
import subprocess
import sys


def parse_plist(path):
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
    print(json.dumps(parse_plist(sys.argv[1])))
```

Now we can run it:

```shell
$ python plist.py ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist
{"LSHandlers": [{"LSHandlerPreferredVersions":...
```

and pipe it to `yq`:

```shell
python plist.py ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist | yq -P
```

to produce YAML:

```yaml
LSHandlers:
  - LSHandlerPreferredVersions:
      LSHandlerRoleAll: '-'
    LSHandlerRoleAll: us.zoom.xos
    LSHandlerURLScheme: zoomphonecall
...
```

We can also make it available everywhere:

```shell
chmod +x plist.py
ln -s $(pwd)/plist.py /usr/local/bin/plist
```

and use it:

```shell
plist path-to-my.plist
```

Enjoy!
