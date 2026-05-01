from rest_framework_api_key.permissions import HasAPIKey


class HasServiceAPIKey(HasAPIKey):
    """API Key para autenticación inter-servicio entre HCM y Nomiweb."""
