"""Compatibility ASGI module; delegates to mentalist_core settings."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mentalist_core.settings")

application = get_asgi_application()
