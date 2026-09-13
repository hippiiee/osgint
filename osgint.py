#!/usr/bin/env python3
# File name          : osgint.py
# Author             : Hippie (@hippiiee_)
# Date created       : 21 Aug 2022

import argparse
import base64
import binascii
import json
import re
import sys

import requests
from requests.auth import HTTPBasicAuth

version_number = "1.1.0"

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
fileJsonOutput = {}
Output = []
emailOutput = []

TARGET_KEYS = {
    "login",
    "id",
    "avatar_url",
    "name",
    "blog",
    "location",
    "twitter_username",
    "email",
    "company",
    "bio",
    "public_gists",
    "public_repos",
    "followers",
    "following",
    "created_at",
    "updated_at",
}


def findReposFromUsername(username):
    response = requests.get(
        f"https://api.github.com/users/{username}/repos?per_page=100&sort=pushed"
    )
    if response.status_code != 200:
        return []
    return [repo["name"] for repo in response.json() if not repo.get("fork")]


def findEmailFromContributor(username, repo, contributor):
    response = requests.get(
        f"https://github.com/{username}/{repo}/commits?author={contributor}",
        auth=HTTPBasicAuth(username, ""),
    ).text
    commit_pattern = rf'href="/{re.escape(username)}/{re.escape(repo)}/commit/(.*?)"'
    latest_commit = re.search(commit_pattern, response)
    if not latest_commit:
        return

    commit_details = requests.get(
        f"https://github.com/{username}/{repo}/commit/{latest_commit.group(1)}.patch",
        auth=HTTPBasicAuth(username, ""),
    ).text
    email = re.search(r"<(.*)>", commit_details)
    if email:
        emailOutput.append(email.group(1))


def findEmailFromUsername(username):
    repos = findReposFromUsername(username)
    for repo in repos:
        findEmailFromContributor(username, repo, username)


def findPublicKeysFromUsername(username, batch=False):
    result = fileJsonOutput[username] if batch else jsonOutput
    gpg_response = requests.get(f"https://github.com/{username}.gpg")
    ssh_response = requests.get(f"https://github.com/{username}.keys")

    if (
        gpg_response.status_code == 200
        and gpg_response.text.strip()
        and "hasn't uploaded any GPG keys" not in gpg_response.text
    ):
        Output.append(f"[+] GPG_keys : https://github.com/{username}.gpg")
        result["GPG_keys"] = f"https://github.com/{username}.gpg"
        # extract email from gpg key
        regex_pgp = re.compile(
            r"-----BEGIN [^-]+-----([A-Za-z0-9+\/=\s]+)-----END [^-]+-----",
            re.MULTILINE,
        )
        matches = regex_pgp.findall(gpg_response.text)
        if matches:
            # Base64 decode the signature block
            b64 = base64.b64decode(matches[0])
            # Convert the base64 to hex
            hx = binascii.hexlify(b64)
            # Get the offsets for the Key ID
            keyid = hx.decode()[48:64]
            Output.append(f"[+] GPG_key_id : {keyid}")
            result["GPG_key_id"] = keyid
            # find email adress
            emails = re.findall(
                r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", b64.decode("Latin-1")
            )
            emailOutput.extend(emails)
    if ssh_response.status_code == 200 and ssh_response.text.strip():
        Output.append(f"[+] SSH_keys : https://github.com/{username}.keys")
        result["SSH_keys"] = f"https://github.com/{username}.keys"


def findInfoFromUsername(username, batch=False):
    if batch:
        fileJsonOutput[username] = {}
    result = fileJsonOutput[username] if batch else jsonOutput
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url)
    except requests.RequestException as error:
        result["error"] = f"GitHub API request failed: {error}"
        return False

    if response.status_code == 200:
        data_keys = response.json()
        for key, value in data_keys.items():
            if key in TARGET_KEYS and value is not None and value != "":
                if key == "email":
                    emailOutput.append(value)
                result[key] = value
                Output.append(f"[+] {key} : {value}")
        result["public_gists"] = f"https://gist.github.com/{username}"
        Output.append(f"[+] public_gists : https://gist.github.com/{username}")
        return True

    if response.status_code == 404:
        result["error"] = "username does not exist"
    else:
        result["error"] = (
            f"GitHub API request failed with status {response.status_code}"
        )
    return False


def findUsernameFromEmail(email):
    response = requests.get("https://api.github.com/search/users", params={"q": email})
    users = response.json().get("items", []) if response.status_code == 200 else []
    if users:
        username = users[0]["login"]
        Output.append(f"[+] username : {username}")
        jsonOutput["username"] = username
    else:
        Output.append("[-] username : Not found")
        jsonOutput["username"] = "Not found"


def clearScanState():
    Output.clear()
    emailOutput.clear()
    jsonOutput.clear()


def findInfoFromFile(input_path, output_path="output.json"):
    fileJsonOutput.clear()
    with open(input_path, "r", encoding="utf-8") as file:
        for username in file:
            username = username.strip()
            if not username:
                continue

            clearScanState()
            username_exists = findInfoFromUsername(username, batch=True)
            if username_exists:
                fullScan(username, batch=True, json_mode=True)

    with open(output_path, "w", encoding="utf-8") as output:
        json.dump(fileJsonOutput, output, sort_keys=True, indent=4)
        output.write("\n")
    print(json.dumps(fileJsonOutput, sort_keys=True, indent=4))
    print(f"[*] Saved results to {output_path}")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog=sys.argv[0], formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument(
        "-u", "--username", default=None, help="GitHub username to search for"
    )
    inputs.add_argument(
        "-e",
        "--email",
        default=None,
        help="Email to use when searching for a GitHub username",
    )
    inputs.add_argument(
        "-i",
        "--input",
        default=None,
        help="Text file containing one GitHub username per line; saves JSON results to output.json",
    )
    parser.add_argument(
        "--json", default=False, action="store_true", help="Return a json output"
    )
    args = parser.parse_args(argv)

    return args


def fullScan(username, batch=False, json_mode=False):
    findEmailFromUsername(username)
    findPublicKeysFromUsername(username, batch)
    if json_mode:
        if batch:
            fileJsonOutput[username]["email"] = sorted(set(emailOutput))
        else:
            jsonOutput["email"] = sorted(set(emailOutput))
            print(json.dumps(jsonOutput, sort_keys=True, indent=4))
    else:
        for data in Output:
            print(data)
        if emailOutput:
            print("[+] email :", end="")
            for email in sorted(set(emailOutput)):
                print(f" {email}", end="")
            print()


def validateInput(args):
    if args.username:
        username_exists = findInfoFromUsername(args.username)
        if username_exists:
            fullScan(args.username, json_mode=args.json)
        else:
            if args.json:
                print(json.dumps(jsonOutput, sort_keys=True, indent=4))
            else:
                print(jsonOutput["error"])
    elif args.input:
        findInfoFromFile(args.input)
    elif args.email:
        findUsernameFromEmail(args.email)
        if args.json:
            print(json.dumps(jsonOutput, sort_keys=True, indent=4))
        else:
            for data in Output:
                print(data)
    else:
        print("Help: ./osgint -h")
        sys.exit(1)


if __name__ == "__main__":
    print(banner)
    args = parse_args()
    validateInput(args)
