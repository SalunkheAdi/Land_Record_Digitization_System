"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.
Also exposes ``app`` for serverless platforms like Vercel.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Alias for Vercel WSGI compatibility
app = application
