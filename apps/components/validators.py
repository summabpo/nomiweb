import re
from django.core.exceptions import ValidationError

def validate_password_format(value):
    if len(value) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", value):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r"\d", value):
        raise ValidationError("La contraseña debe contener al menos un número.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValidationError("La contraseña debe contener al menos un carácter especial.")
    if len(value) > 20:
        raise ValidationError("La contraseña no debe tener más de 20 caracteres.")
