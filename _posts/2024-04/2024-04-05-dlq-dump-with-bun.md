---
title: DLQ dump with Bun
tags: aws aws-cli bun typescript tools
---

Using [`sh()` helper](/bun-shell-multiline) from the previous post we can make a script for 
dumping DLQ locally for inspecting failed events.

```typescript
const queue_url = Bun.argv[2];
(
  await sh(`aws sqs receive-message`, {
    'queue-url': queue_url,
    'max-number-of-messages': 10,
  }).json()
).Messages.forEach(async (msg) => {
  await Bun.write(`messages/${msg.MessageId}.json`, JSON.stringify(msg, null, 2));

  await sh(`aws sqs delete-message`, {
    'queue-url': queue_url,
    'receipt-handle': msg.ReceiptHandle,
  });
})
```

It would be even nicer if one could do

```typescript
await $`${obj} > obj.json`
```

but oh well.

Now we can log all messages with a simple loop:

```typescript
for await (let path of $`ls messages/*.json`.lines()) {
  if (path) console.log(await Bun.file(path).json());
}
```
