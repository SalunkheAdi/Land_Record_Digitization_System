from django import forms
from .models import ValidationAudit


class ValidationAuditForm(forms.ModelForm):
    class Meta:
        model = ValidationAudit
        fields = [
            'parcel', 'inspection_code', 'inspector_name', 'inspection_date',
            'fiscal_year', 'compliance_score', 'risk_level',
            'title_clarity_passed', 'boundary_verification_passed',
            'zoning_compliance_passed', 'encroachment_detected',
            'ai_anomaly_notes', 'final_determination'
        ]
        widgets = {
            'parcel': forms.Select(attrs={'class': 'form-select'}),
            'inspection_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AUD-2024-XXXX'}),
            'inspector_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Officer Name'}),
            'inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fiscal_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'compliance_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'title_clarity_passed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'boundary_verification_passed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'zoning_compliance_passed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'encroachment_detected': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ai_anomaly_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed inspection observations...'}),
            'final_determination': forms.Select(attrs={'class': 'form-select'}),
        }
