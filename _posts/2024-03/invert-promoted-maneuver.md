---
title: Invert promoted maneuver
category: Tools
---

Lower visibility of promoted posts to boost visibility of regular ones:

```html
<style>
div[data-testid="cellInnerDiv"]:has(div[data-testid="placementTracking"]) { opacity: 0.3 }
</style>
```
