from django.contrib import admin
from .models import LandOwner, LandParcel


@admin.register(LandOwner)
class LandOwnerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'national_id', 'phone', 'email', 'parcel_count', 'created_at')
    search_fields = ('first_name', 'last_name', 'national_id', 'phone', 'email')
    list_filter = ('created_at',)
    ordering = ('last_name', 'first_name')


@admin.register(LandParcel)
class LandParcelAdmin(admin.ModelAdmin):
    list_display = (
        'survey_number', 'title_deed_number', 'owner', 'district', 
        'land_type', 'area_sq_meters', 'market_valuation', 
        'digitization_status', 'is_disputed', 'registered_date'
    )
    list_filter = ('digitization_status', 'land_type', 'is_disputed', 'district', 'registered_date')
    search_fields = ('survey_number', 'title_deed_number', 'village', 'district', 'owner__first_name', 'owner__last_name', 'owner__national_id')
    prepopulated_fields = {'slug': ('survey_number',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Cadastral Identity', {
            'fields': ('owner', 'survey_number', 'title_deed_number', 'slug', 'registered_date')
        }),
        ('Geographic Location & Boundary', {
            'fields': ('district', 'taluk', 'village', 'area_sq_meters', 'gis_coordinates')
        }),
        ('Classification & Valuation', {
            'fields': ('land_type', 'market_valuation')
        }),
        ('Status & Verification', {
            'fields': ('digitization_status', 'is_disputed', 'created_at', 'updated_at')
        }),
    )
