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
def iter_account_roles():
    kw = dict(accessToken=get_access_token())
    for account in paginate(
            sso, 'list_accounts',
            **kw, key='accountList', sort=lambda x: x['accountName'],
    ):
        yield account, paginate(
                sso, 'list_account_roles', accountId=account['accountId'],
                **kw, key='roleList',
        )
```

Ok, so now we have the data structure that we need, but before rendering AWS profiles, let's obtain same data using API and CLI.

### AWS API

In order to be able to download and run the script as is, we should avoid dependencies and use Python's standard library. To simplify making HTTP requests, let's make a few helper functions:

```python
import json
import urllib.parse
import urllib.request


def request(*, region, service, path, data=None, method=None, params=None, headers=None):
    query = '?' + urllib.parse.urlencode(params) if params else ''
    data = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(
        method=method or ('POST' if data else 'GET'),
        url=f'https://{service}.{region}.amazonaws.com/{path.lstrip("/")}{query}',
        headers={'Content-type': 'application/json', **(headers or {})},
        data=data,
    )

    class Response:
        def __init__(self, stream):
            self.status_code = stream.status
            self.headers = stream.headers
            self.raw = stream.read()
            self.data = self.error = None
            if self.raw:
                try:
                    self.data = json.loads(self.raw.decode('utf-8'))
                except Exception as err:
                    self.error = err
    try:
        with urllib.request.urlopen(req) as f:
            return Response(f)
    except urllib.request.HTTPError as e:
        return Response(e)


def post(region, service, path, data, **kwargs):
    return request(**kwargs, region=region, service=service, path=path, data=data, method='POST')


def get(region, service, path, **kwargs):
    return request(**kwargs, region=region, service=service, path=path, method='GET')
```

And another one to handle pagination:

```python
import time


def get_all(region, service, path, *, key=None, sort=None, **kwargs):
    results = []
    while True:
        r = get(region=region, service=service, path=path, **kwargs)
        if r.status_code == 429:
            time.sleep(0.2)
            continue
        if r.error:
            raise NotImplementedError(r.error)
        results += r.data[key] if key else r.data
        if t := r.data['nextToken']:
            kwargs.setdefault('params', {}).update({'nextToken': t})
        else:
            break
    if sort:
        results = sorted(results, key=sort)
    return results
```

To get access token we can use the following function:

```python
def get_access_token():
    r = post(SSO_REGION, 'oidc', '/client/register', {
        'clientName': CLIENT_NAME, 'clientType': 'public', 'scopes': [SCOPE],
    })
    kw = {k: r.data[k] for k in ('clientId', 'clientSecret')}
    r = post(SSO_REGION, 'oidc', '/device_authorization', {**kw, 'startUrl': START_URL})
    kw.update(deviceCode=r.data['deviceCode'])
    os.system('open ' + r.data['verificationUriComplete'])
    interval = r.data['interval']
    while True:
        time.sleep(interval)
        r = post(SSO_REGION, 'oidc', '/token', {**kw, 'grantType': GRANT_TYPE})
        if err := r.data.get('error'):
            if err == 'slow_down':
                interval += 5
            elif err != 'authorization_pending':
                raise Exception(r.data)
        else:
            return r.data['accessToken']
```

And for fetching account roles:

```python
def iter_account_roles():
    headers = {'x-amz-sso_bearer_token': get_access_token()}
    for account in get_all(
            SSO_REGION, 'portal.sso', '/assignment/accounts',
            params=dict(max_result=100),
            headers=headers,
            key='accountList',
            sort=lambda a: a['accountName'],
    ):
        yield account, get_all(
            SSO_REGION, 'portal.sso', '/assignment/roles',
            params=dict(max_result=100, account_id=account['accountId']),
            headers=headers,
            key='roleList',
        )
```

### AWS CLI

Let's start with creating a couple of helper functions:

```python
import json
import subprocess


def aws(cmd, key=None, sort=None, **kwargs):
    for k, v in kwargs.items():
        k = k.replace('_', '-')
        cmd += f" --{k}='{v}'"
    cmd = f'/usr/local/bin/aws {cmd}'

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True, check=True, text=True,
        )
    except subprocess.CalledProcessError as e:
        return None, e

    try:
        data = json.loads(proc.stdout)
    except:
        print(proc.stdout)
        raise

    if key:
        assert len(data) == 1, data
        assert key in data, data.keys()
        data = data[key]
    if sort:
        data = sorted(data, key=sort)
    return data, None


def guard(res):
    res, err = res
    if err:
        raise Exception((err, err.sterr, err.stdout))
    return res
```

then get access token:

```python
import time


def get_access_token():
    kw = dict(region=SSO_REGION)
    r = guard(aws('sso-oidc register-client',
                  **kw, client_name=CLIENT_NAME, client_type='public', scopes=SCOPE))
    kw.update(dict(client_id=r['clientId'], client_secret=r['clientSecret']))

    r = guard(aws('sso-oidc start-device-authorization', **kw, start_url=START_URL))
    kw.update(device_code=r['deviceCode'], grant_type=GRANT_TYPE)

    os.system('open ' + r['verificationUriComplete'])

    interval = r['interval']
    while True:
        time.sleep(interval)
        r, err = aws('sso-oidc create-token', **kw)
        if err:
            if 'AuthorizationPendingException' in err.stderr:
                continue
            elif 'SlowDownException' in err.stderr:
                interval += 5
            else:  # i.e. InvalidGrantException
                raise Exception(err.stderr)
        return r['accessToken']
```

and account roles

```python
def iter_account_roles():
    kw = dict(region=SSO_REGION, access_token=get_access_token())
    for account in guard(aws('sso list-accounts', **kw,
                             key='accountList', sort=lambda a: a['accountName'])):
        yield account, guard(aws('sso list-account-roles',
                                 **kw, account_id=account['accountId'], key='roleList'))
```

### AWS config profiles

Now we can proceed to making profile config using the account roles we produced by any of the methods above. Let's iterate data, print profiles and then add default config and SSO session: 

```python
def print_profiles():
    for account, roles in iter_account_roles():
        for role in roles:
            print_profile(
                account_id=account['accountId'],
                account_name=account['accountName'],
                role_name=role['roleName'],
            )
    # also, default and sso-session:
    print(f'''
[default]
region=eu-west-1
output=json

[sso-session sso]
sso_region={SSO_REGION}
sso_registration_scopes={SCOPE}
sso_start_url={START_URL}''')
```

Now we define `print_profile`:

```python
COMMON_PREFIX = 'mycorp-'
IGNORED_ROLES = []


def print_profile(account_id, account_name, role_name):
    if role_name in IGNORED_ROLES:
        return  # skip unnecessary
    profile = account_name.lower().strip().replace(' ', '-').replace(COMMON_PREFIX, '')
    region = guess_region(profile)
    if (rn := role_name) == 'AdministratorAccess':
        profile += '-admin'
    elif rn != 'ReadOnlyAccess':
        profile += '-' + rn
    print(f'''
[profile {profile}]
sso_session=sso
sso_account_id={account_id}
sso_role_name={role_name}
duration_seconds=43200
region={region}''')
```

And we can choose appropriate AWS region guessing from the account name:

```python
def guess_region(profile):
    if profile.endswith('-eu') or profile in ['eu-team']:
        return 'eu-west-3'
    elif profile.endswith(('-us', '-global')) or profile in ['us-team']:
        return 'us-west-2'
    elif profile in ['dev']:
        return 'eu-north-1'
    return 'eu-west-1'
```

Now we can add function call and save all code as e.g. `sso-config.py`:

```python
if __name__ == '__main__':
    print_profiles()
```

Before running AWS SDK variant, we need to install `boto3`:

```shell
python -m venv venv
venv/bin/pip install -U pip
venv/bin/pip install  boto3

venv/bin/python sso-config.py
```

Other methods should work with standard Python distribution:

```shell
python sso-config.py
```

That's it! Let me know what you think:

[Comments](https://twitter.com/afokau/status/1768998128374481120)
