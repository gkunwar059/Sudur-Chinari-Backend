"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os
import re
import django.http.request

# Allow underscores in hostnames for Docker container names (e.g. sudur_backend)
django.http.request.host_validation_re = re.compile(
    r"^([a-z0-9._-]+|\[[a-f0-9]*:[a-f0-9\.:]+\])(:[0-9]+)?$",
    re.IGNORECASE,
)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
