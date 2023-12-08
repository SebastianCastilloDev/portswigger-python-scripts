""" Lab: Username enumeration via different responses """
import re
import requests
LAB_URL = "https://0ae200a703e037d1817cd942004c00b7.web-security-academy.net/"


def main():
    """ Main function """
    print("Login as carlos...", end="")
    data = {"username": "carlos", "password": "montoya"}
    url = LAB_URL + "login"
    r = requests.post(url, data=data, allow_redirects=False, timeout=10)

    session = r.cookies.get("session")
    cookies = {"session": session}
    url = f"{LAB_URL}my-account?id={data['username']}"
    carlos_profile = requests.get(
        url, cookies=cookies, allow_redirects=False, timeout=10)
    pattern = re.findall("Your username is: carlos", carlos_profile.text)
    if len(pattern) != 0:
        print("Congratulations, you solved the lab!")
    else:
        print("Error: cannot login")


if __name__ == "__main__":
    main()
