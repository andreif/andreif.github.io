---
title: Multi-user Git config
tags: git github shell profile tools
---

Having multiple accounts on GitHub (e.g. one private and one or more for work) requires 
setting up either custom hosts or setting per-repo local config. Signed commits would require 
local config anyway, so we can skip messing with hosts and just make a few shell functions to 
help us to configure each repo.

First of all, we will need some global settings. We can configure them to use our private account. 
Assuming we sign private repo commits using SSH format (see [GitHub docs](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key) for details):

```shell
function git-global {
  git config --global user.email 'private@example.com';
  git config --global github.user 'MyPrivateUserName';

  git config --global core.sshCommand 'ssh -i ~/.ssh/github_ed25519 -o IdentitiesOnly=yes';

  git config --global color.ui 'auto'
  git config --global core.excludesFile '~/.gitignore'

  git config --global commit.gpgsign 'true';
  git config --global gpg.program 'gpg';

  git config --global gpg.format 'ssh';
  git config --global user.signingkey '~/.ssh/sign_ed25519.pub';

  git config --global --list | sort;
}

git-global
```

Now let's make a function to configure repo clone from the organization where we use a separate user.
And for this case, let's use PGP signing:

```shell
function git-work1 {
  git config --local user.email 'work1@example.com';
  git config --local github.user 'MyWorkUser1';

  git config --local core.sshCommand 'ssh -i ~/.ssh/work1_ed25519 -o IdentitiesOnly=yes';

  git config --local gpg.format 'openpgp';
  git config --local user.signingkey '...my work key...';

  git config --local --list | sort;
}
```

Now, every time we clone a new repo, we can set its local config by running:

```shell
$ git-work1
```

We can create such function for each org using separate user, e.g. `git-work2` etc.

In case we need to unset the local settings and return to the global config, we can use the following function:

```shell
function git-unset {
  git config --local --unset user.email;
  git config --local --unset github.user;

  git config --local --unset core.sshCommand;

  git config --local --unset gpg.format;
  git config --local --unset user.signingkey;

  git config --local --list | sort;
}
```

### Extras

As a bonus, we can also use the following function to help us with completion and prompt:

```shell
function git-completion() {
  GIT_URL="https://github.com/git/git/raw/v2.39.3";
  echo ${GIT_URL}/contrib/completion/git-completion.bash;
  curl -o ~/git-completion.bash ${GIT_URL}/contrib/completion/git-completion.bash -OL;
  curl -o ~/git-prompt.sh ${GIT_URL}/contrib/completion/git-prompt.sh -OL;
  source ~/git-completion.bash;
}

source ~/git-prompt.sh
```

And also one for making a pretty git log tree:

```shell
function gl() {
  git log $* --decorate --graph --date=short \
  --pretty=format:"%C(yellow)%h%Creset %G? %C(red)%d%Creset %C(green)%an%Creset  %C(cyan)%cr%Creset  %s";
}
```

which can also be defined as an alias:

```shell
git config --global alias.l 'log --decorate --graph  --date=short '\
'--pretty=format:"%C(yellow)%h%Creset %G? %C(red)%d%Creset %C(green)%an%Creset '\
' %C(cyan)%cr%Creset  %s"'
```

and used like this:

```shell
$ git l
$ gl
```

Enjoy!
