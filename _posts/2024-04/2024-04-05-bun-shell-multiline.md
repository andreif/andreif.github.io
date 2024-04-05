---
title: Bun shell for multiline commands
category: Bun
tags: aws-cli bun typescript tools
---

Bun shell [is great](/aws-cli-bun) for shorter commands, but when they become too long, then it gets a bit tricky. 
Thankfully, there is [`{raw: }`](https://bun.sh/docs/runtime/shell#escape-escape-strings) feature, 
that can help us to handle numerous arguments and long commands. 

Let's make a helper function `sh()`:

{% raw %}
```typescript
import { $ } from "bun";

function sh(...args) {
  const raw = args.map((a) => {
    if (Array.isArray(a)) {
      return a.map(String).join(' ');
    } else if (typeof a === 'object') {
      return Object.entries(a).map(([k, v]) => `--${k}="${v}"`).join(' ');
    } else {
      return `${a}`;
    }
  }).join(' ');
  console.log(`$ ${raw}`);
  return $`${{raw}}`;
}
```
{% endraw %}

and then use it for our [SQS example](/aws-cli-bun) from the previous post: 

```typescript
(
  await sh(`aws sqs receive-message`, {
    'queue-url': Bun.argv[2],
    'max-number-of-messages': 10,
  }).json()
).Messages.forEach((msg) => {
  ...
```

Almost perfect! Maybe one day Bun can do it for us out of the box 🤞
