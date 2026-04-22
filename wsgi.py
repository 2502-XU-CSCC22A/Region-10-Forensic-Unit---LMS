"""
WSGI entry-point for the dashboard sub-application.

The project-level WSGI file (config/wsgi.py) is the canonical entry-point
used by Docker / Gunicorn.  This file exists so the dashboard package is
self-contained and can be referenced directly in tooling if needed.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
