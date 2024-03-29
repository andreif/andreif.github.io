---
title: David vs Goliath, or how to keep custom file associations after each Xcode update
category: Tools
tags: macos cli
image:
  path: https://andrei.fokau.se/media/assets/xcode-sublime.webp
---

Updating Xcode/macOS usually resets file type associations and requires reassigning default 
program for them to some other editor that is not as slow and inflexible as Xcode. 
I personally prefer [Sublime Text](https://www.sublimetext.com) and would really like Apple 
to stop constantly messing up my configuration.

## lsregister

Using tips from the article [lsregister: How Files Are Handled in Mac OS X](https://krypted.com/mac-security/lsregister-associating-file-types-in-mac-os-x/) we can automate assigning 
Sublime Text for files we need.

Let's make a soft link to `lsregister` for convenience:

```shell
ln -s /System/Library/Frameworks/CoreServices.framework/Versions/A/Frameworks/LaunchServices.framework/Versions/A/Support/lsregister
```

We can now dump Launch Service database, but since it takes some time, let's dump it to a text file first:

```shell
./lsregister -dump > lsregister.txt  
```

Now, we can determine which programs are associated with specific file types: 

```shell
cat lsregister.txt | grep -E 'bundle id:|claimed UTIs:'
```

and for Xcode specifically:

```shell
$ cat lsregister.txt | grep -E 'bundle id:|claimed UTIs:' | grep 'Xcode (' -A1
bundle id:                  Xcode (0x80c)
claimed UTIs:               public.shell-script, public.bash-script, public.yaml, public.json, ...
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

## Unregister

The article also suggests that one can unregister Xcode, but it seems not possible anymore:

```shell
$ ./lsregister -u /Developer/Applications/Xcode.app
failed to scan /Developer/Applications/Xcode.app: -10814
 from spotlight
```

## defaults read

Since the article was published in 2012, the plist has been moved, so instead of old `~/Library/Preferences/com.apple.LaunchServices.plist` one should use `~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist`.

Let's see what we have there:

```shell
$ defaults read ~/Library/Preferences/com.apple.LaunchServices/com.apple.LaunchServices.secure.plist
{
    LSHandlers =     (
                {
            LSHandlerPreferredVersions =             {
                LSHandlerRoleAll = "-";
            };
            LSHandlerRoleAll = "us.zoom.xos";
            LSHandlerURLScheme = zoomphonecall;
        },
...
```

## defaults write

Let's change default application for `Makefile`:

```shell
$ defaults write com.apple.LaunchServices/com.apple.LaunchServices.secure LSHandlers \
   -array-add '{LSHandlerContentType=public.make-source;LSHandlerRoleAll=com.sublimetext.4;}'

$ defaults read com.apple.LaunchServices/com.apple.LaunchServices.secure | tail -5
            LSHandlerContentType = "public.make-source";
            LSHandlerRoleAll = "com.sublimetext.4";
        }
    );
}
```

Now we have to restart macOS, since relaunching Finder and running the following command does not help:

```shell
./lsregister -kill -r -domain local -domain system -domain user
```

## Test

The following commands should open Sublime Text instead of Xcode. 

```shell
touch Makefile
open Makefile
```

Now we can make a script for opening all common files via our editor.

TBC
