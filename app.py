from flask import Flask, Blueprint, request, jsonify, render_template, request, redirect, url_for
import os
import cv2
import csv
from endpoints.predict import predict_bp
from renamer import rename_images_sequentially

# Define folder for images, CSV file for ratings, and progress file
IMAGES_FOLDER = 'static/images'
CSV_FILE = 'ratings.csv'
PROGRESS_FILE = 'progress.txt'  # File to store the last rated image name

# Define image size for resizing
IMAGE_SIZE = (400, 400)  # Set a larger fixed size for all images

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

app.register_blueprint(predict_bp)

# Create the CSV file if it doesn't exist and add headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['image', 'beauty', 'eyes', 'lips', 'neckline', 'like'])

def get_last_rated_image():
    """
    Lee el archivo de progreso y devuelve el nombre de la última imagen valorada.
    Si el archivo no existe o está vacío, devuelve None.
    """
    # Verificar si el archivo de progreso existe
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            last_image = f.readline().strip()  # Leer la primera línea y eliminar espacios/saltos de línea
            if last_image:  # Si no está vacío, devolver la imagen
                print(f"Última imagen valorada encontrada: {last_image}",  flush=True)
                return last_image
            else:
                print("El archivo de progreso está vacío.")
    else:
        print(f"El archivo de progreso '{PROGRESS_FILE}' no existe.")
    return None

# Function to update the progress file with the last rated image
def update_progress_file(image_name):
    with open(PROGRESS_FILE, 'w') as f:
        f.write(image_name)

# Function to resize an image to a fixed size
def resize_image(image_path, size=IMAGE_SIZE):
    image = cv2.imread(image_path)
    if image is None:
        return None
    resized_image = cv2.resize(image, size)
    cv2.imwrite(image_path, resized_image)  # Overwrite the image with the resized version
    return resized_image

@app.route('/rename', methods=['POST'])
def rename_images():
    """
    Endpoint que llama a la función de renombrado de imágenes.
    """
    # Parámetro `start_index` enviado en la solicitud POST para definir el número inicial
    start_index = request.form.get('start_index', default=1, type=int)
    folder = request.form.get('folder_path', default=1, type=str)

    # Llamar a la función para renombrar las imágenes
    try:
        rename_images_sequentially(folder_path=folder, start_index=start_index)
        return jsonify({"message": "Imágenes renombradas con éxito"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al renombrar las imágenes: {str(e)}"}), 500

# Main route to display image and form
@app.route('/', methods=['GET', 'POST'])
def index():
    # Get list of images in the folder
    image_files = [f for f in os.listdir(IMAGES_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    # Sort the images to process them in order
    image_files.sort()

    # Read the last rated image from the progress file
    last_rated_image = get_last_rated_image()
    print(f"Last Rated Image: {last_rated_image}",  flush=True)
    
    # Determine the starting index based on the last rated image
    if last_rated_image:
        try:
            start_index = image_files.index(last_rated_image) + 1
            print(f"StartIndex: {start_index}",  flush=True)
        except ValueError:
            start_index = 0
    else:
        start_index = 0

    # Filter images that haven't been rated yet
    pending_images = image_files[start_index:]

    # If no images are left to rate, display a message
    if not pending_images:
        return "No more images to rate. Thank you!"

    # Select the first pending image from the list
    current_image = pending_images[0]

    # Resize the current image to a fixed size
    image_path = os.path.join(IMAGES_FOLDER, current_image)
    resize_image(image_path, IMAGE_SIZE)

    if request.method == 'POST':
        # Get the source of the request (which button was clicked)
        action = request.form.get('action')

        # Set default values for beauty, eyes, lips, and neckline
        beauty = request.form.get('beauty', 1)
        eyes = request.form.get('eyes', 1)
        lips = request.form.get('lips', 1)
        neckline = request.form.get('neckline', 1)
        like = False

        # If "Me Gusta" was clicked, set like to True
        if action == 'like':
            like = True

        # If "Descartar" was clicked, set all values to 1 and like to False
        if action == 'discard':
            beauty = eyes = lips = neckline = 1
            like = False

        # Save ratings to the CSV file
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([current_image, beauty, eyes, lips, neckline, like])

        # Update the progress file with the current image name
        update_progress_file(current_image)

        # Redirect to the same page to rate the next image
        return redirect(url_for('index'))

    # Full path to the current image
    image_path = os.path.join(IMAGES_FOLDER, current_image)

    # Render HTML template with the current image
    return render_template('index.html', image=current_image, image_path=image_path)

# Start the application
if __name__ == '__main__':
    app.run(debug=True)
