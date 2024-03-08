---
title: Sharing CloudWatch metrics cross-account
category: AWS
tags: cdk cloudwatch cross-account
---

Using CDK CLI via Docker container as shown in the [previous post](https://andrei.fokau.se/aws-cdk-cli).

Define stack in `app.py`:

```py
import os

from aws_cdk import aws_iam
import aws_cdk


class CloudWatchSharingStack(aws_cdk.Stack):
    def __init__(self, trusted_account_ids: [str], **kwargs) -> None:
        super().__init__(**kwargs)
        aws_iam.Role(
            scope=self,
            id="Role",
            role_name='CloudWatch-CrossAccountSharingRole',
            assumed_by=aws_iam.CompositePrincipal(
                *(aws_iam.AccountPrincipal(account_id) for account_id in trusted_account_ids)
            ),
            description="A role for sharing CloudWatch metrics across accounts",
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(name) for name in (
                    'CloudWatchReadOnlyAccess',
                    'CloudWatchAutomaticDashboardsAccess',
                    'AWSXrayReadOnlyAccess',
                )
            ],
        )


app = aws_cdk.App()
CloudWatchSharingStack(
    scope=app,
    id="CloudWatchSharingStack",
    stack_name="CloudWatchSharingStack",
    env=aws_cdk.Environment(
        account=os.environ['CDK_DEFAULT_ACCOUNT'],
        region=os.environ['CDK_DEFAULT_REGION'],
    ),
    trusted_account_ids=['123456789012'],
)
app.synth()
```

and create a `Makefile`:

```makefile
clean:
	rm -rf cdk.out
	rm -rf venv

venv:
	cdk.sh -c 'python -m venv venv && venv/bin/pip install -U pip'
	cdk.sh -c 'venv/bin/pip install  aws-cdk-lib  constructs'
	echo "$$(yq -Moj '.app = "venv/bin/python app.py"' cdk.json)" > cdk.json

synth: venv
	cdk synth | yq -P
```

The following `cdk.json` would also work in our case:

```json
{
  "app": "venv/bin/python app.py"
}
```

Now synth the template:

```shell
make clean synth
```

Locking dependencies is a good idea for a more complex or regularly-updated stack, `requirements.txt`

```requirements
aws-cdk-lib==2.131.0
constructs>=10.0.0,<11.0.0
```

To make inspections work in PyCharm, one could create a host venv and use it for interpreter 

```makefile
venv_host:
	python -m venv venv_host
	venv_host/bin/pip install -U pip
	venv_host/bin/pip install -r requirements.txt
	
...:
	cdk.sh -c 'venv/bin/pip install -r requirements.txt'
```
