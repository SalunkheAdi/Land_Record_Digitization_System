from django.urls import path
from . import views

urlpatterns = [
    # Public & Authentication Routes
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Cadastral Operations & Dashboards (Protected)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('parcels/', views.parcel_list_view, name='parcel_list'),
    path('parcel/add/', views.parcel_create_view, name='parcel_create'),
    path('parcel/<slug:slug>/', views.parcel_detail_view, name='parcel_detail'),
    path('parcel/<int:pk>/edit/', views.parcel_update_view, name='parcel_update'),
    path('parcel/<int:pk>/delete/', views.parcel_delete_view, name='parcel_delete'),
    path('parcels/district/<str:district>/', views.parcels_by_district_view, name='parcels_by_district'),
    path('owners/', views.owner_list_view, name='owner_list'),
    path('owners/add/', views.owner_create_view, name='owner_create'),
]
