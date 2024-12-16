#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File name          : osgint.py
# Author             : Hippie (@hippiiee_)
# Date created       : 21 Aug 2022

from email.mime import base
import json
import requests
import binascii
import re
from requests.auth import HTTPBasicAuth
import sys
import base64
import argparse

version_number = '1.0.3'

banner = f"""\x1b[0;33m
 .d88888b.                    d8b          888
d88P" "Y88b                   Y8P          888
888     888                                888
888     888 .d8888b   .d88b.  888 88888b.  888888
888     888 88K      d88P"88b 888 888 "88b 888
888     888 "Y8888b. 888  888 888 888  888 888
Y88b. .d88P      X88 Y88b 888 888 888  888 Y88b.
 "Y88888P"   88888P'  "Y88888 888 888  888  "Y888
                          888  \x1b[1;33mv{version_number}\x1b[0;33m
                     Y8b d88P
                      "Y88P"
\x1b[0;1;3mBy Hippie\x1b[0;33m | \x1b[0;1mhttps://twitter.com/hiippiiie\x1b[0m
"""

jsonOutput = {}
output = []
email_out = []

def findReposFromUsername(username):
    response = requests.get('https://api.github.com/users/%s/repos?per_page=100&sort=pushed' % username).text
    repos = re.findall(r'"full_name":"%s/(.*?)",.*?"fork":(.*?),' % username, response)
    nonForkedRepos = []
    for repo in repos:
        if repo[1] == 'false':
            nonForkedRepos.append(repo[0])
    return nonForkedRepos


def findEmailFromContributor(username, repo, contributor):
    response = requests.get('https://github.com/%s/%s/commits?author=%s' % (username, repo, contributor), auth=HTTPBasicAuth(username, '')).text
    latestCommit = re.search(r'href="/%s/%s/commit/(.*?)"' % (username, repo), response)
    if latestCommit:
        latestCommit = latestCommit.group(1)
    else:
        latestCommit = 'dummy'
    commitDetails = requests.get('https://github.com/%s/%s/commit/%s.patch' % (username, repo, latestCommit), auth=HTTPBasicAuth(username, '')).text
    email = re.search(r'<(.*)>', commitDetails)
    if email:
        email = email.group(1)
        email_out.append(email)
    return

def findEmailFromUsername(username):
	repos = findReposFromUsername(username)
	for repo in repos:
		findEmailFromContributor(username, repo, username)

def findPublicKeysFromUsername(username):
    gpg_response = requests.get(f'https://github.com/{username}.gpg').text
    ssh_response = requests.get(f'https://github.com/{username}.keys').text
    breakpoint()
    if not "hasn't uploaded any GPG keys" in gpg_response:
        output.append(f'[+] GPG_keys : https://github.com/{username}.gpg')
        jsonOutput['GPG_keys'] = f'https://github.com/{username}.gpg'
        # extract email from gpg key
        regex_pgp = re.compile(r"-----BEGIN [^-]+-----([A-Za-z0-9+\/=\s]+)-----END [^-]+-----", re.MULTILINE)
        matches = regex_pgp.findall(gpg_response)
        if matches:
            # Base64 decode the signature block
            b64 = base64.b64decode(matches[0])
            # Convert the base64 to hex
            hx = binascii.hexlify(b64)
            # Get the offsets for the Key ID
            keyid = hx.decode()[48:64]
            output.append(f'[+] GPG_key_id : {keyid}')
            jsonOutput['GPG_key_id'] = keyid
            # find email adress
            emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", b64.decode('Latin-1'))
            if emails:
                for email in emails:
                    email_out.append(email)
    if ssh_response :
        output.append(f'[+] SSH_keys : https:/github.com/{username}.keys')
        jsonOutput['SSH_keys'] = f'https://github.com/{username}.keys'

def findInfoFromUsername(username):
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url)
    if response.status_code == 200 and requests.codes.ok:
        data = response.json()
        for i in data:
            if i in ['login','id','avatar_url','name','blog','location','twitter_username','email','company','bio','public_gists','public_repos','followers','following','created_at','updated_at']:
                if data[i] != None and data[i] != '':
                    if i == 'email':
                        email_out.append(data[i])
                    jsonOutput[i] = data[i]
                    output.append(f'[+] {i} : {data[i]}')
        jsonOutput['public_gists'] = f'https://gist.github.com/{username}'
        output.append(f'[+] public_gists : https://gist.github.com/{username}')
        return True
    elif response.status_code == 404:
        jsonOutput['error'] = 'username does not exist'
        return False

def findUsernameFromEmail(email):
    response = requests.get('https://api.github.com/search/users?q=%s' % email).text
    username = re.findall(r'"login":"(.*?)"', response)
    if username:
        output.append(f'[+] username : {username[0]}')
        jsonOutput['username'] = username[0]
    else:
        output.append(f'[-] username : Not found')
        jsonOutput['username'] = 'Not found'

class CustomParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('Error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse_args():
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-u", "--username", default=None, help="Github username of the account to search for")
    parser.add_argument("-e", "--email", default=None, help="Email of the account to search for github username")
    parser.add_argument("--json", default=False, action="store_true", help="Return a json output")
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    print(banner)
    args = parse_args()
    if(args.username):
        username_exists = findInfoFromUsername(args.username)
        if username_exists:
            findEmailFromUsername(args.username)
            findPublicKeysFromUsername(args.username)
            if(args.json):
                jsonOutput['email'] = list(set(email_out))
                print(json.dumps(jsonOutput, sort_keys=True, indent=4))
            else:
                for data in output:
                    print(data)
                if email_out != []:
                    print('[+] email :', end='')
                    for email in list(set(email_out)):
                        print(f' {email}', end='')
        else:
            if(args.json):
                print(json.dumps(jsonOutput, sort_keys=True, indent=4))
            else:
                print(f'Username does not exist')
    elif(args.email):
        findUsernameFromEmail(args.email)
        if(args.json):
            print(json.dumps(jsonOutput, sort_keys=True, indent=4))
        else:
            for data in output:
                print(data)
    else:
        print('Help: ./osgint -h')
        sys.exit(1)
