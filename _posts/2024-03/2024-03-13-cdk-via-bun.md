---
title: Segmentation fault for AWS CDK in Bun
category: JS/TS
tags: bun aws-cdk cli docker typescript
image:
  path: https://andrei.fokau.se/media/assets/bun-segfault-cdk.webp
---

Unfortunately testing AWS CDK with Bun failed using the image from the [previous post](/bun-via-docker): 

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

### Update 1.0.31
Still failing.

But to be fair, CDK does not like it from the start showing warning:
```
!!  This software has not been tested with node v21.6.0.
```
