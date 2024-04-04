---
title: Using AWS CLI with Bun
category: AWS
tags: aws-cli bun typescript tools
---

In order to use both AWS CLI and Bun together, we need to put them on the same image. We can use [`public.ecr.aws/aws-cli/aws-cli`](https://gallery.ecr.aws/aws-cli/aws-cli) as base and then add the Bun binary. 

The standard way of installing Bun is:

```shell
curl -fsSL https://bun.sh/install | bash
```

but for our narrow use-case we can just pick relevant commands from the script:

```dockerfile
FROM public.ecr.aws/aws-cli/aws-cli

RUN yum update -y && \
    yum install -y unzip && \
    yum clean all

ARG TARGET=linux-x64
ARG URL=https://github.com/oven-sh/bun/releases/latest/download/bun-${TARGET}.zip

RUN curl -fLo /tmp/bun.zip "${URL}" && \
    unzip -o /tmp/bun.zip -d /tmp && \
    mv /tmp/bun-${TARGET}/bun /usr/local/bin/ && \
    rm -r /tmp/bun*

ENTRYPOINT []
CMD ["bash"]
```

We can build it for macOS and M1 processor using the following command:

```shell
docker build --build-arg TARGET=linux-aarch64 --platform=linux/aarch64 -t amz_bun .
```

Let's create a Makefile for convenience:

```makefile
SHELL = bash
tag = aws-cli-bun
run = docker run --rm -ti --env-file <(env | grep AWS_) -v "$$(pwd):/app" -w /app ${tag}
bun = ${run} bun

build:
	docker build --build-arg TARGET=linux-aarch64 --platform=linux/aarch64 -t ${tag} .

run:
	${run}

version:
	${bun} -v
```

Now, let's use it for something useful. For example, to log some events from a DLQ. 

Create a script `dlq-cli.ts`:

```typescript
import { $ } from "bun";

(
  await $`aws sqs receive-message --queue-url ${Bun.argv[2]} --max-number-of-messages 10`.json()
).Messages.forEach((msg) => {
  const body = JSON.parse(msg.Body);
  if (body.detail) {
    console.log("BUS", body.detail)
  } else if (body.Message) {
    console.log("SNS", JSON.parse(body.Message))
  } else {
    console.log("???", body)
  }
})
```

and then add a couple of targets to Makefile:

```makefile
dlq-cli:
	@${bun} dlq-cli.ts ${QUEUE_URL}
	
account1-dlq:
	@aws-vault exec account1-profile -- make dlq-cli QUEUE_URL="https://..."

account2-dlq:
	@aws-vault exec account2-profile -- make dlq-cli QUEUE_URL="https://..."
```

So now we can easily run it:

```shell
$ make account1-dlq
SNS {
  ...
}
```

Feels good, man!
