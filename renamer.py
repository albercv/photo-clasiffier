import os

def rename_images_sequentially(folder_path='downloaded_images', start_index=551):
    """
    Renombra todos los archivos .jpg en la carpeta especificada con nombres secuenciales 
    a partir del valor de `start_index`.
    
    Args:
        folder_path (str): Ruta a la carpeta que contiene las imágenes a renombrar.
        start_index (int): Número inicial para el nombre secuencial (por ejemplo, 1 para comenzar en 000001.jpg).
        
    Returns:
        None
    """
    # Obtener una lista de todos los archivos .jpg en la carpeta
    jpg_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.jpg')])

    print(f"FolderPath: {folder_path}")
    
    # Recorrer cada archivo y cambiarle el nombre
    for index, filename in enumerate(jpg_files, start=start_index):
        # Definir el nuevo nombre secuencial en formato 000001.jpg, 000002.jpg, etc.
        new_name = f"{index:04}.jpg"
        
        # Obtener la ruta completa de origen y destino
        src = os.path.join(folder_path, filename)
        dst = os.path.join(folder_path, new_name)
        
        # Renombrar el archivo
        os.rename(src, dst)
        print(f"Renombrado: {filename} -> {new_name}")