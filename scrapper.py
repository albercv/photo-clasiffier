import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# Parámetros configurables
SEARCH_QUERY = 'big breast woman'  # Variable para definir la búsqueda
START_INDEX = 1000  # Número inicial para el nombre de las imágenes
NUMBER_OF_IMAGES = 500  # Número de imágenes que quieres descargar
OUTPUT_FOLDER = 'downloaded_images'  # Carpeta donde se guardarán las imágenes

# Crear la carpeta de salida si no existe
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Encabezados para la solicitud (user-agent) para evitar ser bloqueado por Google
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# Contador para el nombre secuencial de las imágenes
counter = START_INDEX
current_page = 0

while counter - START_INDEX < NUMBER_OF_IMAGES:
    # Construir la URL de búsqueda con el parámetro 'start' para la paginación
    search_url = f"https://www.google.com/search?tbm=isch&q={SEARCH_QUERY}&start={current_page * 20}"
    print(f"Buscando en URL: {search_url}")

    # Realizar la solicitud a la página de búsqueda
    response = requests.get(search_url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error al acceder a la URL: {search_url}")
        break

    # Analizar la página HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraer enlaces de imágenes usando tanto 'src' como 'data-src'
    image_tags = soup.find_all('img')

    for i, img_tag in enumerate(image_tags):
        # Si ya hemos descargado el número deseado de imágenes, detener la descarga
        if counter - START_INDEX >= NUMBER_OF_IMAGES:
            break

        # Obtener la URL de la imagen desde 'src' o 'data-src'
        img_url = img_tag.get('data-src') or img_tag.get('src')
        if not img_url or not img_url.startswith('http'):
            continue

        try:
            # Realizar la solicitud para obtener la imagen
            img_response = requests.get(img_url, headers=HEADERS, timeout=5)
            if img_response.status_code == 200:
                # Abrir y guardar la imagen en formato JPG con nombre secuencial
                img = Image.open(BytesIO(img_response.content))
                img_name = f"{OUTPUT_FOLDER}/{counter:06}.jpg"
                img.convert('RGB').save(img_name, 'JPEG')
                print(f"Imagen guardada: {img_name}")
                counter += 1
        except Exception as e:
            print(f"Error al descargar la imagen {img_url}: {e}")

    # Incrementar el índice de la página actual para avanzar en la paginación
    current_page += 1
    print(f"Avanzando a la siguiente página ({current_page}).")

print(f"Descarga completada. {counter - START_INDEX} imágenes guardadas en '{OUTPUT_FOLDER}'.")
