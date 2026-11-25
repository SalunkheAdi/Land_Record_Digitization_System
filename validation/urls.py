from django.urls import path, re_path
from . import views

urlpatterns = [
    path('validations/', views.validation_list_view, name='validation_list'),
    path('validation/inspect/<int:parcel_id>/', views.validation_create_view, name='validation_create'),
    path('land-prediction/', views.land_prediction_view, name='land_prediction'),
    path('land-prediction/<int:prediction_id>/sync-audit/', views.sync_prediction_to_audit_view, name='sync_prediction_to_audit'),
    path('api/land-prediction/', views.api_predict_land, name='api_predict_land'),
    path('api/parcels/<slug:slug>/validate/', views.api_validate_parcel, name='api_validate_parcel'),
    path('api/ai-agent/query/', views.ai_agent_chat_api, name='ai_agent_chat_api'),
    re_path(r'^audit/fiscal-year/(?P<year>20\d{2})/$', views.audit_fiscal_year_view, name='audit_fiscal_year'),
]
