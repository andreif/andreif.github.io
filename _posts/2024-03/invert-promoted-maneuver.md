---
title: Invert promoted maneuver
category: Tools
tags: css ads
date: 2024-03-02 16:30:00 +0100
---

Lower visibility of promoted posts to boost visibility of regular ones:

```html
<style>
div[data-testid="cellInnerDiv"]:has(div[data-testid="placementTracking"]) { opacity: 0.3 }
</style>
```
