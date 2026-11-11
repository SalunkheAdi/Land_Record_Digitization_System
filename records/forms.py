from django import forms
from .models import LandOwner, LandParcel


class LandOwnerForm(forms.ModelForm):
    class Meta:
        model = LandOwner
        fields = ['first_name', 'last_name', 'national_id', 'email', 'phone', 'residential_address']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ramesh'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kumar'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. NID-8892-4410'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ramesh.kumar@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +91 9876543210'}),
            'residential_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full residential address'}),
        }


class LandParcelForm(forms.ModelForm):
    class Meta:
        model = LandParcel
        fields = [
            'owner', 'title_deed_number', 'survey_number', 'district', 
            'taluk', 'village', 'area_sq_meters', 'land_type', 
            'market_valuation', 'gis_coordinates', 'is_disputed', 
            'digitization_status', 'registered_date'
        ]
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'title_deed_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. TD-2024-8831'}),
            'survey_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. SY-104-2B'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bengaluru Urban'}),
            'taluk': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. North Taluk'}),
            'village': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Hebbal'}),
            'area_sq_meters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'land_type': forms.Select(attrs={'class': 'form-select'}),
            'market_valuation': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000.00'}),
            'gis_coordinates': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.9716 N, 77.5946 E'}),
            'is_disputed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'digitization_status': forms.Select(attrs={'class': 'form-select'}),
            'registered_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
