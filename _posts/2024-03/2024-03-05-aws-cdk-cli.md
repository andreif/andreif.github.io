---
title: Setting up AWS CDK CLI
category: AWS
tags: cdk
---

## Using local Node.js

Install NVM as described on 
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
	echo '#!/usr/bin/env bash\n. ~/.nvm/nvm.sh && ./node_modules/aws-cdk/bin/cdk $$*' > cdk
	chmod +x cdk
```

## Using Docker image

Create `Dockerfile`:

```dockerfile
FROM node:20-alpine
RUN npm install -g aws-cdk
```

Make cdk binary running cdk image:

```makefile
cdk:
	docker build -t aws-cdk .
	echo '#!/usr/bin/env bash\ndocker run --rm -it -v $$(pwd):/home -w /home aws-cdk cdk $$*' > cdk
	chmod +x cdk
```

Test it

```sh
$ ./cdk --version
2.131.0 (build 92b912d)
```
