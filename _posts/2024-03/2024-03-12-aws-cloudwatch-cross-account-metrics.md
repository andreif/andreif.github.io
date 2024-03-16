---
title: Sharing CloudWatch metrics cross-account (part 2)
category: AWS
tags: aws-cdk cloudwatch cross-account python
---

[Part 1](/aws-cloudwatch-cross-account) shows how to enable cross-account access using role suggested by AWS.

Let's make it more secure by limiting:
- trust relationships for that role to only CloudWatch cross-account service,
- and permissions to only metrics. 

```py
from aws_cdk import aws_iam
import aws_cdk


class CloudWatchSharingStack(aws_cdk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        actions = [
            'cloudwatch:GetMetricData',
            'cloudwatch:GetMetricStatistics',
            'cloudwatch:ListMetrics',
        ]
        service_role = '/'.join([
            'aws-service-role',
            'cloudwatch-crossaccount.amazonaws.com',
            'AWSServiceRoleForCloudWatchCrossAccount',
        ])
        aws_iam.Role(
            scope=self,
            id="Role",
            role_name='CloudWatch-CrossAccountSharingRole',
            assumed_by=aws_iam.CompositePrincipal(
                *(
                    aws_iam.ArnPrincipal(f'arn:aws:iam::{account_id}:role/{service_role}')
                    for account_id in self.node.get_context('TrustedAccountIds').split(',')
                )
            ),
            description="A role for sharing CloudWatch metrics across accounts",
            inline_policies={
                'AllowMetrics': aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            effect=aws_iam.Effect.ALLOW,
                            actions=actions,
                            resources=['*'],
                        ),
                    ],
                ),
            },
        )
```
