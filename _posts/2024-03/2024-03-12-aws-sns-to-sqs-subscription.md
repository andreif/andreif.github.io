---
title: Subscribing SQS Queue to SNS Topic cross-account
category: AWS
tags: aws-cdk python cross-account sns sqs
---

Example stack for subscribing to topics from various accounts from a single consumer account:

```python
from aws_cdk import aws_sns, aws_sqs, aws_lambda, aws_lambda_event_sources, aws_sns_subscriptions
import aws_cdk

TOPICS = {
    'my-event-eu': 'arn:aws:sns:eu-north-1:12345689012:my-event',
    'my-event-us': 'arn:aws:sns:us-east-1:34568901234:my-event',
}

class TopicSubscriptionStack(aws_cdk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        log_lambda = aws_lambda.Function(
            scope=self,
            id="EventLogFunction",
            function_name="EventLogFunction",
            handler='main.lambda_handler',
            runtime=aws_lambda.Runtime.PYTHON_3_12,
            code=aws_lambda.Code.from_asset('./lambda'),
        )

        for event_name, topic_arn in TOPICS.items():
            topic = aws_sns.Topic.from_topic_arn(
                scope=self,
                id=f"Topic-{event_name}",
                topic_arn=topic_arn,
            )
            queue = aws_sqs.Queue(
                scope=self,
                id=f"EventQueue-{event_name}",
                queue_name=f'EventQueue-{event_name}',
                visibility_timeout=aws_cdk.Duration.seconds(60),
            )
            dlq = aws_sqs.Queue(
                scope=self,
                id=f"EventDLQ-{event_name}",
                queue_name=f'EventDLQ-{event_name}',
            )
            topic.add_subscription(
                aws_sns_subscriptions.SqsSubscription(
                    queue=queue,
                    dead_letter_queue=dlq,
                    raw_message_delivery=True,
                )
            )
            log_lambda.add_event_source(
                aws_lambda_event_sources.SqsEventSource(queue=queue)
            )
```
