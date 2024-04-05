---
title: Bun CLI via Docker
category: Bun
tags: bun cli docker typescript
---

Similarly to how [AWS CDK CLI is used with Docker](/aws-cdk-cli), we can run Bun too:

```makefile
#.PHONY: bun
bun:
	docker pull oven/bun
	export sh='#!/usr/bin/env bash\n' \
	  && echo $${sh}'docker run --rm -it --init -v "$$(pwd):/home/bun/app" \\' > bun_run \
	  && echo ' --env-file <(env | grep AWS_) -p 3000:3000 oven/bun "$$@"' >> bun_run \
	  && echo $${sh}'"$${BASH_SOURCE[0]}_run" bun "$$@"' > bun
	chmod +x bun bun_run

/usr/local/bin/bun: bun
	ln -sf "$$(pwd)/bun_run" /usr/local/bin/
	ln -sf "$$(pwd)/bun" /usr/local/bin/
	ls -l /usr/local/bin/bun*

setup: /usr/local/bin/bun

# The following targets are here just for easy one-click running in PyCharm:
bash: setup
	bun_run bash
version: setup
	bun -v
```
