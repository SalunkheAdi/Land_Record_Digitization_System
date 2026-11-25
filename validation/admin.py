from django.contrib import admin
from .models import ValidationAudit, LandPrediction


@admin.register(ValidationAudit)
class ValidationAuditAdmin(admin.ModelAdmin):
    list_display = (
        'inspection_code', 'parcel', 'inspector_name', 'inspection_date',
        'fiscal_year', 'compliance_score', 'risk_level', 'final_determination'
    )
    list_filter = ('final_determination', 'risk_level', 'fiscal_year', 'inspection_date')
    search_fields = ('inspection_code', 'inspector_name', 'parcel__survey_number', 'parcel__title_deed_number')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Inspection Identity', {
            'fields': ('parcel', 'inspection_code', 'inspector_name', 'inspection_date', 'fiscal_year')
        }),
        ('AI & Compliance Assessment', {
            'fields': ('compliance_score', 'risk_level', 'final_determination')
        }),
        ('Verification Checkpoints', {
            'fields': ('title_clarity_passed', 'boundary_verification_passed', 'zoning_compliance_passed', 'encroachment_detected')
        }),
        ('Remarks & Documentation', {
            'fields': ('ai_anomaly_notes', 'created_at')
        }),
    )


@admin.register(LandPrediction)
class LandPredictionAdmin(admin.ModelAdmin):
    list_display = (
        'survey_number', 'safety_status', 'predicted_health_score',
        'determination', 'vegetation_ratio', 'builtup_ratio',
        'audit_logged', 'created_at'
    )
    list_filter = ('safety_status', 'determination', 'audit_logged', 'created_at')
    search_fields = ('survey_number', 'ai_analysis_summary')
    readonly_fields = ('created_at',)

