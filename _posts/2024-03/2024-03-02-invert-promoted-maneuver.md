---
title: Invert promoted maneuver
category: Tools
tags: css browser extension
date: 2024-03-02 16:30:00 +0100
---

Create a `manifest.json`

```json
{
    "name": "WebX",
    "permissions": ["activeTab", "webNavigation"],
    "version": "0.1.0",
    "description": "Web Experience",
    "manifest_version": 3,
    "host_permissions": [
        "https://twitter.com/*", "https://x.com/*"
    ],
    "content_scripts": [
        {
            "matches": ["https://twitter.com/*", "https://x.com/*"],
            "css": ["css/x.css"],
            "run_at": "document_end"
        }
    ],
    "icons": {}
}
```

Create `css/x.css` to boost visibility of regular posts by lowering opacity of promoted ones:

```css
div[data-testid="cellInnerDiv"]:has(div[data-testid="placementTracking"]) { opacity: 0.3 }
```
