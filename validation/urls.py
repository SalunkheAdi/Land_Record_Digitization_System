from django.urls import path, re_path
from . import views

urlpatterns = [
    path('validations/', views.validation_list_view, name='validation_list'),
    path('validation/inspect/<int:parcel_id>/', views.validation_create_view, name='validation_create'),
    path('api/parcels/<slug:slug>/validate/', views.api_validate_parcel, name='api_validate_parcel'),
    re_path(r'^audit/fiscal-year/(?P<year>20\d{2})/$', views.audit_fiscal_year_view, name='audit_fiscal_year'),
]
