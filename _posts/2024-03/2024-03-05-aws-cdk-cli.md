---
title: Setting up AWS CDK CLI
category: AWS
tags: cdk
---

## Using local Node.js

Install NVM as described in 
[https://github.com/nvm-sh/nvm?#installing-and-updating](https://github.com/nvm-sh/nvm?#installing-and-updating)

In your `Makefile`:

```makefile
clean:
	rm -rf cdk
	rm -rf node_modules

cdk:
	. ~/.nvm/nvm.sh \
	  && nvm install 20 \
	  && npm install -g npm@latest \
	  && npm install aws-cdk
	echo '#!/usr/bin/env bash\n. ~/.nvm/nvm.sh\nnvm use 20' > cdk
	echo '$$(dirname "$${BASH_SOURCE[0]}")/node_modules/aws-cdk/bin/cdk $$*' >> cdk
	chmod +x cdk
```

## Using Docker image

Create `Dockerfile`:

```dockerfile
FROM node:20-alpine
RUN apk add --no-cache python3 py3-pip
RUN npm install -g aws-cdk
```

Make cdk binary running cdk image:

```makefile
cdk:
	docker build -t aws-cdk .
	export run='#!/usr/bin/env bash\ndocker run --rm -it -v "$$(pwd):/home" -w /home aws-cdk' \
	  && echo $${run}' cdk "$$@"' > cdk \
	  && echo $${run}' sh "$$@"' > cdk.sh
	chmod +x cdk cdk.sh
	./cdk --version
	./cdk.sh -c 'cdk --version'
```

## Shell setup

Add a similar line to your shell profile so that `cdk` is found globally

```shell
export PATH="/Users/andrei/Projects/AWS-CDK-CLI:$PATH"
```

## Testing

Check version

```sh
$ cd /tmp && cdk --version
2.131.0 (build 92b912d)
```

Init a new stack

```shell
# 1. Init stack
mkdir -p demo && cd demo
cdk init app --language python

# 2a. Install dependencies using Node
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt

# 2b. or using Docker
cdk.sh -c '.venv/bin/python -m pip install -U pip'
cdk.sh -c '.venv/bin/python -m pip install -r requirements.txt'

# 3. Patch config
echo "$(yq -M -oj '.app = ".venv/bin/python3 app.py"' cdk.json)" > cdk.json

# 4. Synth CloudFormation template
cdk synth | yq -P
```
