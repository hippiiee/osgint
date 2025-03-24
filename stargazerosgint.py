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

# ================================
# Part 1: Get stargazer usernames
# ================================
def get_stargazer_usernames(target):
    import stargazerz
    # Create a Crawler instance with 16 threads for the given target repository.
    crawler = stargazerz.Crawler(threads=16, target=target)
    # Run the crawler to fetch the stargazer data.
    try:
        crawler.run()
    except ValueError as e:
        if "range() arg 3 must not be zero" in str(e):
            print("Fewer stargazers than threads detected. Re-running crawler with threads=1.")
            crawler.threads = 1
            crawler.run()
        else:
            raise e
    # Return the list of stargazer usernames.
    return crawler.stargazers

# ============================================
# Part 2: Username search functions (osgint)
# ============================================

# Global variables used in these functions
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
    url = 'https://github.com/%s/%s/commits?author=%s' % (username, repo, contributor)
    response = requests.get(url, auth=HTTPBasicAuth(username, '')).text
    latestCommit = re.search(r'href="/%s/%s/commit/(.*?)"' % (username, repo), response)
    if latestCommit:
        latestCommit = latestCommit.group(1)
    else:
        latestCommit = 'dummy'
    commit_url = 'https://github.com/%s/%s/commit/%s.patch' % (username, repo, latestCommit)
    commitDetails = requests.get(commit_url, auth=HTTPBasicAuth(username, '')).text
    email = re.search(r'<(.*)>', commitDetails)
    if email:
        email_out.append(email.group(1))
    return

def findEmailFromUsername(username):
    repos = findReposFromUsername(username)
    for repo in repos:
        findEmailFromContributor(username, repo, username)

def findPublicKeysFromUsername(username):
    gpg_response = requests.get(f'https://github.com/{username}.gpg').text
    ssh_response = requests.get(f'https://github.com/{username}.keys').text
    if "hasn't uploaded any GPG keys" not in gpg_response:
        output.append(f'[+] GPG_keys : https://github.com/{username}.gpg')
        jsonOutput['GPG_keys'] = f'https://github.com/{username}.gpg'
        regex_pgp = re.compile(r"-----BEGIN [^-]+-----([A-Za-z0-9+\/=\s]+)-----END [^-]+-----", re.MULTILINE)
        matches = regex_pgp.findall(gpg_response)
        if matches:
            b64 = base64.b64decode(matches[0])
            hx = binascii.hexlify(b64)
            keyid = hx.decode()[48:64]
            output.append(f'[+] GPG_key_id : {keyid}')
            jsonOutput['GPG_key_id'] = keyid
            emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", b64.decode('Latin-1'))
            if emails:
                for email in emails:
                    email_out.append(email)
    if ssh_response:
        output.append(f'[+] SSH_keys : https://github.com/{username}.keys')
        jsonOutput['SSH_keys'] = f'https://github.com/{username}.keys'

def findInfoFromUsername(username):
    url = f'https://api.github.com/users/{username}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        for key in data:
            if key in ['login', 'id', 'avatar_url', 'name', 'blog', 'location', 'twitter_username', 
                       'email', 'company', 'bio', 'public_gists', 'public_repos', 'followers', 
                       'following', 'created_at', 'updated_at']:
                if data[key]:
                    if key == 'email':
                        email_out.append(data[key])
                    jsonOutput[key] = data[key]
                    output.append(f'[+] {key} : {data[key]}')
        jsonOutput['public_gists'] = f'https://gist.github.com/{username}'
        output.append(f'[+] public_gists : https://gist.github.com/{username}')
        return True
    elif response.status_code == 404:
        jsonOutput['error'] = 'username does not exist'
        return False

# =======================================
# Part 3: Main: Process Usernames and Save
# =======================================
def main():
    # Specify the target repository (in "owner/repo" format) to fetch stargazers.
    target_repo = "edithturn/ArrowGIFsCollection"  # Change this to your desired target
    print(f"Fetching stargazer usernames for repository: {target_repo}")
    stargazer_usernames = get_stargazer_usernames(target_repo)
    print(f"Retrieved {len(stargazer_usernames)} usernames.")

    all_results = []
    # Process each username using the username search functions.
    for username in stargazer_usernames:
        # Reinitialize global variables for each username
        global jsonOutput, output, email_out
        jsonOutput = {}
        output = []
        email_out = []
        print(f"--- Searching for username: {username} ---")
        exists = findInfoFromUsername(username)
        if exists:
            findEmailFromUsername(username)
            findPublicKeysFromUsername(username)
        jsonOutput["searched_value"] = username
        jsonOutput["search_type"] = "username"
        all_results.append(jsonOutput.copy())

    # Write results to a text file (each line is a JSON object)
    out_filename = "username_results.txt"
    with open(out_filename, "w") as f:
        for res in all_results:
            f.write(json.dumps(res) + "\n")
    print(f"Results saved to {out_filename}")

if __name__ == "__main__":
    print(banner)
    main()
