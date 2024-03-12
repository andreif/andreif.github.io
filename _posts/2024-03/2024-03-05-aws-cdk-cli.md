---
title: Setting up AWS CDK CLI
category: AWS
tags: cdk cli docker
---

Reference guide by AWS:
[https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html](https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html)

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
	export sh='#!/usr/bin/env bash\n' \
	  && echo $${sh}'docker run --rm -it -v "$$(pwd):/home" -w /home aws-cdk "$$@"' > cdk_run \
	  && echo $${sh}'"$${BASH_SOURCE[0]}_run" cdk "$$@"' > cdk
	chmod +x cdk cdk_run
	./cdk --version
```

## Shell setup

Add a similar line to your shell profile so that `cdk` is found globally:

```shell
export PATH="/Users/andrei/Projects/AWS-CDK-CLI:$PATH"
```

## Testing

Check version:

```sh
$ cd .. && cdk --version
2.131.0 (build 92b912d)
```

Init a new stack:

```shell
# 1. Init stack
mkdir -p demo && cd demo
cdk init app --language python

# 2a. Install dependencies created using local Node cdk
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt

# 2b. or using Docker
cdk_run python -m venv .venv
cdk_run .venv/bin/pip install -U pip
cdk_run .venv/bin/pip install -r requirements.txt

# 3. Patch config
echo "$(yq -Moj '.app = ".venv/bin/python app.py"' cdk.json)" > cdk.json

# 4. Synth CloudFormation template
cdk synth | yq -P
```

## AWS session

In order to call AWS API we need to pass AWS session to the container.

`aws-vault` allows creating a metadata service server on port 9099 so for standard 
AWS CLI we could add `-p 9099:9099` to the `docker run` parameters but CDK CLI does not 
support it and honestly, the service is too implicit to be considered safe when working 
with multiple accounts.

Instead, we can pass all environmental variables with names starting with `AWS_` prefix:

```shell
--env-file <(env | grep ^AWS_)
```

so that our run command in `cdk_run` file will look like:

```shell
docker run --rm -it -v "$(pwd):/home" -w /home --env-file <(env | grep ^AWS_) aws-cdk "$@"
```

and we can run `cdk deploy` the following way:

```shell
aws-vault exec my-profile -- cdk deploy
```
