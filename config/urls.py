"""
URL configuration for config project.
Academic Task: INT253 - Web Development in Python Using Django
Project: Intelligent Land Record Digitization and Validation System
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('records.urls')),
    path('', include('validation.urls')),
]

handler404 = 'records.views.custom_404_view'
handler500 = 'records.views.custom_500_view'
