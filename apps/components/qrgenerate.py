import qrcode
from io import BytesIO
from base64 import b64encode

"""
Funciones para la Generación de Códigos QR

Esta función está diseñada para generar un código QR con los datos proporcionados y devolverlo en formato HTML como una imagen embebida en base64.

1. `generate_qr_code(data)`
    Genera un código QR a partir de los datos proporcionados y lo convierte en una imagen en formato base64 para ser usada en HTML.

    Parámetros
    ----------
    data : str
        Los datos que se codificarán en el código QR. Pueden ser cualquier tipo de cadena de texto (URL, texto, etc.).

    Retorna
    -------
    str
        Un string con el código HTML necesario para mostrar el código QR como una imagen embebida en base64.

    Descripción
    -----------
    Esta función crea un código QR a partir de los datos proporcionados y lo convierte en una imagen en formato PNG. Luego, codifica esta imagen en base64 y genera un código HTML para que la imagen pueda ser mostrada directamente en una página web. El tamaño del código QR es ajustado automáticamente.

    Ejemplo
    -------
    generate_qr_code("https://example.com") -> '<img src="data:image/png;base64,iVBORw0KGgoAAAANS..." alt="QR Code">'
"""


def generate_qr_code(data):
    # Creamos un objeto QRCode
    qr = qrcode.QRCode(
        version=1,  # Tamaño del código QR (1-40)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel de corrección de errores
        box_size=10,  # Tamaño de cada "cuadro" en el código QR
        border=4,  # Ancho del borde del código QR
    )

    # Añadimos los datos al objeto QRCode
    qr.add_data(data)
    qr.make(fit=True)

    # Creamos un objeto BytesIO para almacenar la imagen del código QR
    qr_img = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(qr_img)

    # Convertimos la imagen del código QR a base64
    qr_img_base64 = b64encode(qr_img.getvalue()).decode()

    # Creamos el código HTML para mostrar la imagen del código QR
    html = f'<img src="data:image/png;base64,{qr_img_base64}" alt="QR Code">'
    
    return html
