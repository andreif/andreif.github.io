---
title: Segmentation fault for AWS CDK via Bun
category: JS/TS
tags: bun cdk cli docker typescript
---

Unfortunately testing AWS CDK with Bun failed: 

```makefile
.PHONY: demo
demo:
	rm -rf demo
	mkdir -p demo && cd demo \
	  && bun x cdk init app --language typescript \
	  && bun install \
	  && perl -pi -e 's/npx ts-node --prefer-ts-exts/bun/g' cdk.json \
	  && bun x cdk synth
```

```
Segmentation fault

Subprocess exited with error 139
make: *** [Makefile:4: demo] Error 1
```

and the following when running via bash within the container

```
Killed

Subprocess exited with error 137
```
