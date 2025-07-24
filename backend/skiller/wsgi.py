"""
WSGI config for skiller project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skiller.settings')

application = get_wsgi_application()
