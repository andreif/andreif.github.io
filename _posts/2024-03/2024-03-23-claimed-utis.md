---
title: David vs Goliath, or how to keep custom file associations after each Xcode update
category: Tools
tags: macos cli
image:
  path: https://andrei.fokau.se/media/assets/xcode-sublime.webp
---

Updating Xcode usually resets file type associations and requires reassigning default 
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

Also, after it was published in 2012, the plist has been moved/changed and instead of old `~/Library/Preferences/com.apple.LaunchServices.plist` there are two files now:

```shell
$ ls -1 ~/Library/Preferences/com.apple.LaunchServices/
com.apple.LaunchServices.SettingsStore.sql
com.apple.LaunchServices.plist
com.apple.launchservices.secure.plist
```

not giving any meaningful info:

```shell
$ defaults read ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices
{
    "Architectures for arm64" =     {
...

$ defaults read ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure
{
    LSHandlers =     (
                {
            LSHandlerPreferredVersions =             {
                LSHandlerRoleAll = "-";
            };
            LSHandlerRoleAll = "com.apple.gamecenter.gamecenteruiservice";
            LSHandlerURLScheme = gamecenter;
        },
...
```

## defaults write

Using suggested command we can create `~/Library/Preferences/com.apple.LaunchServices.plist`:

```shell
$ defaults write com.apple.LaunchServices LSHandlers \
    -array-add '{LSHandlerContentType=public.make-source;LSHandlerRoleAll=com.sublimetext.4;}'

$ ls -1 ~/Library/Preferences/com.apple.LaunchServices*
/Users/andrei/Library/Preferences/com.apple.LaunchServices.QuarantineEventsV2
/Users/andrei/Library/Preferences/com.apple.LaunchServices.plist

/Users/andrei/Library/Preferences/com.apple.LaunchServices:
com.apple.LaunchServices.SettingsStore.sql
com.apple.LaunchServices.plist
com.apple.launchservices.secure.plist
```

So reading it returns our config now:

```shell
$ defaults read com.apple.LaunchServices
{
    LSHandlers =     (
                {
            LSHandlerContentType = "public.make-source";
            LSHandlerRoleAll = "com.sublimetext.4";
        }
    );
}
```

However, it did not changed anything and `open Makefile` still opens the file in Xcode even 
after restarting Finder and running:

```shell
./lsregister -kill -r -domain local -domain system -domain user
```

Same after changing the existing plists:

```shell
$ defaults write com.apple.LaunchServices/com.apple.LaunchServices LSHandlers \
    -array '{LSHandlerContentType=public.make-source;LSHandlerRoleAll=com.sublimetext.4;}'

$ defaults write com.apple.LaunchServices/com.apple.LaunchServices.secure LSHandlers \
    -array '{LSHandlerContentType=public.make-source;LSHandlerRoleAll=com.sublimetext.4;}'
```

TBC
