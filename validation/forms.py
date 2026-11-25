from django import forms
from .models import ValidationAudit, LandPrediction


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


class LandPredictionForm(forms.Form):
    """
    Form for uploading cadastral survey number and land/satellite image
    for AI Land Health & Safety prediction.
    """
    PRESET_CHOICES = [
        ('', '-- Or select an instant 1-Click AI aerial sample --'),
        ('clean_agricultural', '🌾 Clean Agricultural Land (Lush Crops, Clear Canals)'),
        ('ecological_wetland', '🌊 Ecological Wetland / Conservation Buffer'),
        ('disputed_encroached', '⚠️ Disputed Land (Encroachment & Concrete Incursions)'),
    ]

    survey_number = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g. SY-104-2B, SY-99-DISP, or any survey number',
            'id': 'id_survey_number',
            'autocomplete': 'off'
        }),
        help_text="Enter an official survey number (e.g., SY-104-2B) or any parcel identifier."
    )
    image_file = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'id_image_file',
            'accept': 'image/*'
        }),
        help_text="Upload satellite, aerial drone, or ground photo of the land parcel."
    )
    preset_sample = forms.ChoiceField(
        choices=PRESET_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_preset_sample'
        }),
        help_text="For fast testing during presentations, select a pre-calibrated sample."
    )
    preset_image_data = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_preset_image_data'})
    )

    def clean(self):
        cleaned_data = super().clean()
        image_file = cleaned_data.get('image_file')
        preset_sample = cleaned_data.get('preset_sample')
        preset_image_data = cleaned_data.get('preset_image_data')

        if not image_file and not preset_sample and not preset_image_data:
            raise forms.ValidationError("Please upload a land image or select one of the instant aerial presets.")

        return cleaned_data

