# OSGINT
<p align="center">
  Retrieve informations about a github username/email
  <br>
      <img alt="img last release" src="https://img.shields.io/github/release/hippiie/ogsint.svg?color=blue">
  <a href="https://twitter.com/intent/follow?screen_name=hiippiiie" title="Follow"><img src="https://img.shields.io/twitter/follow/hiippiiie?label=hiippiiie&style=social"></a>
  <br>
</p>

## Features
  - [x] Find github username from an email
  - [x] Find email from github username (not working all the time)
  - [x] Find informations about a profile (account creation date, public gists, id, public pgp, public ssh ...)
## Requirements

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
                          888  v1.0.0
                     Y8b d88P                     
                      "Y88P"                      
By Hippie | https://twitter.com/hiippiiie

usage: osgint.py [-h] [-u USERNAME] [-e EMAIL] [--json]

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Github username of the account to search for (default: None)
  -e EMAIL, --email EMAIL
                        Email of the account to search for github username (default: None)
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

## How does it works ?

To get a user email, osingt is checking :
 - all the public commits of the user, if the email is not hidden in one of the commit it will be added to the list
 - if the user have a GPG key, if he has one, it's getting the email from the content of the GPG after a base64 decode
 - github user API

To get a user email, osgint is checking :
 - github user API
 - 🚧 spoofing a commit with the email, then checking the name in the commit history (working every time) 🚧 (Work In Progress)

*Project inspired from [Zen](https://github.com/s0md3v/Zen)*
