from django.apps import AppConfig

class BerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'disposal'  # <--- CHECK THIS LINE. It likely says 'ber' right now.
