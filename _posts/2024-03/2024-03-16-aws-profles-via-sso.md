---
title: Generating AWS profiles using API, CLI, and Python SDK
category: AWS
tags: aws-cdk aws-cli aws-api python aws-vault aws-sso
image:
  path: /assets/img/sso-profiles.webp
---

After being assigned permissions via [AWS Identity Center](https://aws.amazon.com/iam/identity-center/), one would need to create profiles in `~/.aws/config` file in order to be able to use them with [AWS CLI](https://aws.amazon.com/cli/) and/or [aws-vault](https://github.com/99designs/aws-vault), e.g.:

```shell
aws-vault exec my-profile -- aws sts get-caller-identity
```

### Official guide from AWS

To create profiles one could follow the [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html) and run the following CLI commands

```shell
aws configure sso
# or
aws configure sso-session
aws sso login --sso-session $name
```

As the guide mentions, the configuration can be set manually too in `~/.aws/config` file. This can be done more efficiently via a script if the number of profiles is large, or if they need to be regularly updated/synced.

Let's make a Python script to generate current profiles. We can use either SDK, API, or CLI, so let's see how do it with each of them.

In all cases we will need a few constants:

```python
import os

SSO_REGION = os.environ.get('SSO_REGION', 'eu-north-1')
SSO_ID = os.environ['SSO_ID']
START_URL = f'https://{SSO_ID}.awsapps.com/start'
SCOPE = 'sso:account:access'
GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:device_code'
# The client name will be shown on the oauth page: 
CLIENT_NAME = 'Andrei'
```

### AWS SDK for Python (boto3)

With SDK we will use `sso` and `sso-oidc` services:

```python
import boto3

aws = (session := boto3.Session(region_name=SSO_REGION).client)
sso_oidc = aws('sso-oidc')
sso = aws('sso')
```

Let's define a function to retrieve access token:

```python
import time


def get_access_token():
    r = sso_oidc.register_client(clientName=CLIENT_NAME, clientType='public', scopes=[SCOPE])
    kw = {k: r[k] for k in ('clientId', 'clientSecret')}

    r = sso_oidc.start_device_authorization(**kw, startUrl=START_URL)
    kw.update(deviceCode=r['deviceCode'])

    # Open URL, sign-in via OIDC, and then click on the authorize buttons:
    os.system('open ' + r['verificationUriComplete'])

    interval = r['interval']
    while True:
        time.sleep(interval)
        try:
            return sso_oidc.create_token(**kw, grantType=GRANT_TYPE)['accessToken']
        except sso_oidc.exceptions.InvalidGrantException:
            exit(1)  # e.g. token has expired
        except sso_oidc.exceptions.AuthorizationPendingException:
            pass
        except sso_oidc.exceptions.SlowDownException:
            interval += 5
```

#### Paginator

Now, we will need to paginate SDK responses, which can sometimes return an empty list and a pointer to the next page:

```python
def paginate(client, cmd, **kwargs):
    key = kwargs.pop('key', None)
    sort = kwargs.pop('sort', None)
    results = [
        result
        for page in client.get_paginator(cmd).paginate(**kwargs)
        for result in (page[key] if key else page)
    ]
    if sort:
        results = sorted(results, key=sort)
    return results
```

We can use it to fetch all accounts and their roles:

```python
def get_account_roles():
    kw = dict(access_token=get_access_token())
    result = {}
    for acc in paginate(
            sso, 'list_accounts',
            **kw, key='accountList', sort=lambda x: x['accountName'],
    ):
        roles = paginate(
                sso, 'list_account_roles', accountId=acc['accountId'],
                **kw, key='roleList',
        )
        result[acc['accountId']] = {
            'name': acc['accountName'],
            'roles': [r['roleName'] for r in roles],
        }
    return result
```

Ok, so now we have the data structure that we need and before rendering AWS profiles, let's obtain same data using API and CLI.

TBC...
