#!/bin/bash
# Build script for Vercel deployment
echo "=== Installing Dependencies ==="
python3 -m pip install -r requirements.txt

echo "=== Collecting Static Files ==="
python3 manage.py collectstatic --noinput --clear

echo "=== Applying Database Migrations ==="
python3 manage.py migrate --noinput
