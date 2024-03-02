---
layout: post
title: Perfect dark mode theme for GitHub Pages with Jekyll 
# date: 2024-02-29 17:00:00 +0100
categories: Static
tags: jekyll dark-mode github-pages
image:
  path: /assets/img/jekyll.webp
---

## Original guide

[Watch Video](https://www.youtube.com/watch?v=F8iOU1ci19Q) and read [Meet Jekyll - The Static Site Generator](https://technotim.live/posts/jekyll-docs-site/) by Techno Tim.
{% include embed/youtube.html id='F8iOU1ci19Q' %}

## Fixes and workarounds

Sign in to GitHub and [use this template][use-template] to generate a brand new repository and name it
`USERNAME.github.io`, where `USERNAME` represents your GitHub username.

Then change version in `Gemfile` to work around a recent issue:

```ruby
gem "jekyll-theme-chirpy", "~> 6.4.2"
```

Add the following steps between `Setup Ruby` and `Build site` to avoid local clone & bundle.

```yml
      - name: Bundle
        run: bundle

      - name: Lock
        run: cat Gemfile.lock
```

You can later commit `Gemfile.lock` to lock the dependencies and can always see the versions in action run history.

Also, choose Page deploy via workflow to avoid double action run.

[Customize favicons](https://chirpy.cotes.page/posts/customize-the-favicon/)


## Better code blocks

Create `/assets/css/jekyll-theme-chirpy.scss` to use some opionated syntax highlighting improvements.

```scss
---
---

@import 'main';

/* append your custom style below */

@media (prefers-color-scheme: dark) {
  html:not([data-mode]), html[data-mode=dark], * {
    .highlight {
      pre {
        font-size: .70rem;
      }
      .nf {
        color: #079bd9;
      }
      .o, .mi, .mf {
        color: #3792b8 !important;
      }
      .p {
        color: #69a1b9 !important;
      }
      .k, .kn, .kr, .kp, .kv, .ow {
        color: rgb(255, 123, 114) !important;
      }
      .c, .c1, .cm {
        color: #525252 !important;
      }
    }
  }
}

.code-header button:hover {
  background-color: transparent !important;
}
.code-header button {
  border: none !important;
}

.highlight .lineno {
  opacity: 0.2;
}

.sidebar-bottom {
  .icon-border {
    opacity: 0;
  }
}

.embed-video {
  max-width: 500px;
}
```

References:
 - [https://github.com/mzlogin/rouge-themes?tab=readme-ov-file#base16dark](https://github.com/mzlogin/rouge-themes?tab=readme-ov-file#base16dark)
 - [https://github.com/cotes2020/jekyll-theme-chirpy/blob/master/_sass/colors/syntax-dark.scss](https://github.com/cotes2020/jekyll-theme-chirpy/blob/master/_sass/colors/syntax-dark.scss)


## Example of Python code syntax highlighting

```py
import re
import wsgiref.simple_server as ss
import urllib.parse

1.0  # float

def match_route(path, routes):
    for pattern, handler in routes.items():
        if path == pattern:
            return handler, {}
        elif pattern.startswith('^') and (match := re.match(pattern, path)):
            return handler, {"match": match}


def respond(handler, status=200, **kwargs):
    args = ()
    if isinstance(handler, tuple):
        status, response, *args = handler
    elif callable(handler):
        response = handler(**kwargs)
        if isinstance(response, tuple):
            status, response, *args = response
    else:
        response = handler
    return status, response, *args
```

[Comment](https://twitter.com/afokau/status/1763875089492169152) on <i class="fa-brands fa-x-twitter"></i>

[use-template]: https://github.com/cotes2020/chirpy-starter/generate
