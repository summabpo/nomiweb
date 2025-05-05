import re
from django.core.exceptions import ValidationError

"""
Valida que la contraseña cumpla con ciertos criterios de seguridad: longitud mínima, presencia de mayúsculas, números, caracteres especiales y longitud máxima.

### Función `validate_password_format(value)`

Esta función recibe una contraseña y valida que cumpla con los requisitos mínimos de seguridad para ser considerada válida. Si la contraseña no cumple con alguno de los criterios establecidos, lanza una excepción `ValidationError` con el mensaje correspondiente.

#### Parámetros:
- `value` (str): La contraseña que se desea validar.

#### Excepciones:
- Lanza un `ValidationError` si alguno de los siguientes criterios no se cumple:
  - La contraseña debe tener al menos 8 caracteres.
  - La contraseña debe contener al menos una letra mayúscula.
  - La contraseña debe contener al menos un número.
  - La contraseña debe contener al menos un carácter especial (por ejemplo, `!@#$%^&*(),.?":{}|<>`).
  - La contraseña no debe tener más de 20 caracteres.

#### Descripción:
La función realiza una serie de comprobaciones usando expresiones regulares para verificar que la contraseña proporcionada cumpla con los siguientes requisitos:
1. **Longitud mínima**: La contraseña debe tener al menos 8 caracteres.
2. **Letra mayúscula**: La contraseña debe contener al menos una letra mayúscula (`[A-Z]`).
3. **Número**: La contraseña debe contener al menos un número (`\d`).
4. **Carácter especial**: La contraseña debe contener al menos un carácter especial. Se busca en una lista de caracteres especiales comunes como `!@#$%^&*(),.?":{}|<>`.
5. **Longitud máxima**: La contraseña no debe exceder los 20 caracteres.

Si alguna de las condiciones no se cumple, se lanza una excepción `ValidationError` con un mensaje detallado que indica qué regla no se ha cumplido.

#### Ejemplo de Uso:
```python
validate_password_format("Password123!")  # No lanza excepción si la contraseña es válida.
validate_password_format("pass")  # Lanza ValidationError por longitud mínima y otros criterios.


#### Excepciones:
ValidationError: Se lanza si la contraseña no cumple con alguna de las condiciones de validación.

"""

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
