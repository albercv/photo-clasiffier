import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, Flatten, Concatenate, Input
from tensorflow.keras.models import Model
from flask import Blueprint, request, jsonify
from tensorflow.keras.applications import VGG16

# Crear el blueprint para el endpoint de predicción
predict_bp = Blueprint('predict', __name__)

# Ruta donde se guardará el modelo
MODEL_PATH = 'models/combined_model.h5'

def create_default_model():
    """
    Crea un modelo básico con dos entradas (imágenes y atributos) y lo guarda en la ruta especificada.
    """
    # Definir la entrada de las imágenes (por ejemplo, 224x224 imágenes con 3 canales de color)
    img_input = Input(shape=(224, 224, 3), name='img_input')

    # Cargar el modelo preentrenado VGG16 para extraer características de las imágenes
    vgg_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

    # Congelar las capas del modelo base para no entrenarlas de nuevo
    for layer in vgg_model.layers:
        layer.trainable = False

    # Aplicar el modelo preentrenado a la entrada de imágenes
    x = vgg_model(img_input)
    x = Flatten()(x)
    x = Dense(256, activation='relu')(x)
    x = Dropout(0.5)(x)

    # Definir la parte del modelo que procesará los atributos
    attr_input = Input(shape=(4,), name='attr_input')
    y = Dense(16, activation='relu')(attr_input)
    y = Dropout(0.5)(y)

    # Combinar ambas entradas (imagen y atributos)
    combined = Concatenate()([x, y])
    z = Dense(64, activation='relu')(combined)
    z = Dropout(0.5)(z)
    output = Dense(1, activation='sigmoid')(z)  # Salida binaria (like o no like)

    # Crear el modelo completo
    model = Model(inputs=[img_input, attr_input], outputs=output)

    # Compilar el modelo
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Crear la carpeta 'models' si no existe
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # Guardar el modelo en el archivo .h5
    model.save(MODEL_PATH)
    print(f"Modelo creado y guardado en: {MODEL_PATH}")

# Verificar si el archivo del modelo existe, si no, crearlo
if not os.path.exists(MODEL_PATH):
    print(f"El archivo {MODEL_PATH} no existe. Creando un modelo por defecto...")
    create_default_model()
else:
    print(f"El archivo {MODEL_PATH} ya existe. Cargando el modelo...")
    model = tf.keras.models.load_model(MODEL_PATH)

# Definir el endpoint /predict
@predict_bp.route('/predict', methods=['POST'])
def predict():
    # Verificar si se envió un archivo con la solicitud
    if 'image' not in request.files:
        return jsonify({"error": "No se envió ninguna imagen"}), 400

    file = request.files['image']

    # Leer la imagen enviada por el usuario
    image = np.array(tf.keras.preprocessing.image.img_to_array(tf.keras.preprocessing.image.load_img(file, target_size=(224, 224))))
    image = np.expand_dims(image, axis=0)  # Expandir dimensiones para que sea compatible con el modelo
    image = tf.keras.applications.vgg16.preprocess_input(image)  # Preprocesar la imagen como lo haría VGG16

    # Atributos de ejemplo (pueden ser calculados o predefinidos)
    attributes = np.array([[3, 3, 3, 3]], dtype='float32')  # Placeholder, aquí deberías pasar los atributos reales

    # Hacer la predicción con el modelo híbrido
    prediction = model.predict([image, attributes])

    # Determinar si la imagen te gusta o no
    like = bool(prediction[0] > 0.5)

    # Devolver la predicción y los atributos calculados
    return jsonify({
        "like": like,
        "attributes": {
            "beauty": attributes[0][0],
            "eyes": attributes[0][1],
            "lips": attributes[0][2],
            "neckline": attributes[0][3]
        }
    })
