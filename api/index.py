"""
Vercel Serverless WSGI Entrypoint for Django
Intelligent Land Record Digitization and Validation System
"""

import os
import sys
from pathlib import Path

# Set up project root directory in Python path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Mark environment as Vercel
os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application

# Vercel's Python runtime requires a callable named 'app'
app = get_wsgi_application()
