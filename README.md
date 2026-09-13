# OSGINT
<p align="center">
  Retrieve public information about a GitHub username or email address
  <br>
      <img alt="img last release" src="https://img.shields.io/github/v/release/hippiiee/osgint.svg?color=blue">
  <a href="https://twitter.com/intent/follow?screen_name=hiippiiie" title="Follow"><img src="https://img.shields.io/twitter/follow/hiippiiie?label=hiippiiie&style=social"></a>
  <br>
</p>

## Features
  - [x] Find a GitHub username from an email address
  - [x] Find email addresses associated with a GitHub username (not always available)
  - [x] Find public profile information (account creation date, public gists, ID, GPG keys, SSH keys, etc.)
  - [x] Scan a list of GitHub usernames and save the results as JSON
## Requirements

- Python 3.10 or newer

```bash
pip3 install -r requirements.txt
```
## Usage

```
$ python3 osgint.py -h                                  

 .d88888b.                    d8b          888    
d88P" "Y88b                   Y8P          888    
888     888                                888    
888     888 .d8888b   .d88b.  888 88888b.  888888 
888     888 88K      d88P"88b 888 888 "88b 888    
888     888 "Y8888b. 888  888 888 888  888 888    
Y88b. .d88P      X88 Y88b 888 888 888  888 Y88b.  
 "Y88888P"   88888P'  "Y88888 888 888  888  "Y888 
                          888  v1.1.0
                     Y8b d88P                     
                      "Y88P"                      
By Hippie | https://twitter.com/hiippiiie

usage: osgint.py [-h] [-u USERNAME | -e EMAIL | -i INPUT] [--json]

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Github username of the account to search for (default: None)
  -e EMAIL, --email EMAIL
                        Email of the account to search for github username (default: None)
  -i INPUT, --input INPUT
                        Text file containing one GitHub username per line; saves JSON results to output.json (default: None)
  --json                Return a json output (default: False)
```
## Example output
### username
```bash
$ ./osgint.py -u hippiiee
[+] login : hippiiee
[+] id : 41185722
[+] avatar_url : https://avatars.githubusercontent.com/u/41185722?v=4
[+] name : Hippie
[+] blog : https://hippie.cat
[+] bio : Hi !
[+] public_repos : 10
[+] public_gists : 0
[+] followers : 8
[+] following : 9
[+] created_at : 2018-07-13T08:28:00Z
[+] updated_at : 2022-08-21T13:11:36Z
[+] public_gists : https://gist.github.com/hippiiee
[+] GPG_keys : https://github.com/hippiiee.gpg
[+] GPG_key_id : 27cbb171ff857c58
[+] email : hquere@e3r4p3.42.fr hippolyte.q@gmail.com
```

```json
$ ./osgint.py -u hippiiee --json
{
    "GPG_key_id": "27cbb171ff857c58",
    "GPG_keys": "https://github.com/hippiiee.gpg",
    "avatar_url": "https://avatars.githubusercontent.com/u/41185722?v=4",
    "bio": "Hi !",
    "blog": "https://hippie.cat",
    "created_at": "2018-07-13T08:28:00Z",
    "email": [
        "hquere@e3r4p3.42.fr",
        "hippolyte.q@gmail.com"
    ],
    "followers": 8,
    "following": 9,
    "id": 41185722,
    "login": "hippiiee",
    "name": "Hippie",
    "public_gists": "https://gist.github.com/hippiiee",
    "public_repos": 10,
    "updated_at": "2022-08-21T13:11:36Z"
}
```

### Email
``` bash
$ ./osgint.py -e chrisadr@gentoo.org
[+] username : ChrisADR
```
```json
$ ./osgint.py -e chrisadr@gentoo.org --json
{
    "username": "ChrisADR"
}
```

### Input file

Provide one username per line. Empty lines and surrounding whitespace are ignored.

```text
hippiiee
torvalds
```

```bash
$ ./osgint.py --input usernames.txt
```

The combined JSON result is printed and saved to `output.json`.

## How does it work?

To find email addresses associated with a username, OSGINT checks:
 - the user's public commits
 - email addresses included in the user's public GPG keys
 - the GitHub user API

To find a GitHub username from an email address, OSGINT checks:
 - the GitHub user search API
 - 🚧 spoofing a commit with the email, then checking the name in the commit history (working every time) 🚧 (Work In Progress)

*Project inspired from [Zen](https://github.com/s0md3v/Zen)*
