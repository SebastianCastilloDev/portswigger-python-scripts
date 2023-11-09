import requests # Permite hacer la peticion GET
from bs4 import BeautifulSoup # Permite extraer datos del html

# Parámetros de entrada
url = ""

# Realizamos la petición GET
respuesta = requests.get(url)

# Nos traemos todos los h3
extraerDatos=BeautifulSoup(respuesta.text, 'html.parser')
productos=extraerDatos.findAll('h3')

print("Resultados: Conteo y lista de productos\n")
print("Cantidad: " + str(len(productos)) + " productos\n")
print("Listado de productos")
print("--------------------")

for producto in productos:
    print (producto.get_text())