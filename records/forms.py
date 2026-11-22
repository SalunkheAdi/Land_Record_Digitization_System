from django import forms
from django.contrib.auth.models import User
from .models import LandOwner, LandParcel


class UserRegistrationForm(forms.ModelForm):
    """
    User registration / sign-up form with password confirmation,
    input validation, and Bootstrap styling matching the cartographic palette.
    """
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'autofocus': True
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create strong password'
        }),
        min_length=6,
        help_text='Minimum 6 characters.'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose username (letters, numbers, underscores)'
            })
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Please provide a valid username.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Please provide a valid email address.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean_first_name(self):
        return self.cleaned_data.get('first_name', '').strip()

    def clean_last_name(self):
        return self.cleaned_data.get('last_name', '').strip()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username'].strip()
        user.email = self.cleaned_data['email'].strip().lower()
        user.first_name = self.cleaned_data['first_name'].strip()
        user.last_name = self.cleaned_data['last_name'].strip()
        user.set_password(self.cleaned_data['password'])
        user.is_active = True
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    Clean user sign-in form with Bootstrap styling.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )


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
