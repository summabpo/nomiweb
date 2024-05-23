import qrcode
from io import BytesIO
from base64 import b64encode

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
