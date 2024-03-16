---
title: Generating AWS profiles using SDK, API, and CLI
category: AWS
tags: aws-cdk aws-cli aws-api python aws-vault aws-sso
---

After being assigned permissions via [AWS Identity Center](https://aws.amazon.com/iam/identity-center/), one would need to create profiles in `~/.aws/config` file in order to be able to use them with [AWS CLI](https://aws.amazon.com/cli/) and/or [aws-vault](https://github.com/99designs/aws-vault), e.g.:

```shell
aws-vault exec my-profile -- aws sts get-caller-identity
```

To create profiles one could follow the [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html) and run the following CLI commands

```shell
aws configure sso
# or
aws configure sso-session
aws sso login --sso-session $name
```

As the guide mentions, the configuration can be set manually too in `~/.aws/config` file, which can be more efficiently done via script if the number of profiles is large, or if they need to be regularly updated/synced.

Let's make a Python script to generate current profiles.

TBC...
