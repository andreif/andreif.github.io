---
title: David vs Goliath, or how to keep custom file associations after each Xcode update
category: Tools
tags: macos cli
---

Updating Xcode usually resets file type associations and requires reassigning default 
program for them to some other editor that is not as slow and inflexible as Xcode. 
I personally prefer Sublime Text and would really like Apple to stop constantly messing 
up my configuration.

Using tips from the article [lsregister: How Files Are Handled in Mac OS X](https://krypted.com/mac-security/lsregister-associating-file-types-in-mac-os-x/) we can automate assigning 
Sublime Text for files we need.

Let's make a soft link to `lsregister` for convenience:

```shell
ln -s /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister
```

We can now dump Launch Service database, but since it takes some time, let's dump it to a text file first:

```shell
./lsregister --dump > lsregister.txt  
```

Now, we can determine which programs are associated with specific file types: 

```shell
cat lsregister.txt | grep -E 'bundle id:|claimed UTIs:'
```

In order to see what Uniform Type Identifier (UTI) corresponds to a given filename extension, 
we can use metadata list utility `mdls`:

```shell
$ mdls Makefile
_kMDItemDisplayNameWithExtensions  = "Makefile"
...
kMDItemContentType                 = "public.make-source"
kMDItemContentTypeTree             = (
    "public.make-source",
    "public.script",
    "public.source-code",
    "public.plain-text",
    "public.text",
    "public.data",
    "public.item",
    "public.content"
)
...
```

or specifically for `kMDItemContentType`:

```shell
$ mdls -name kMDItemContentType Makefile
kMDItemContentType = "public.make-source"
```

TBC
