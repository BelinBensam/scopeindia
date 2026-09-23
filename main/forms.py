import re
from datetime import date
from django import forms
from django.contrib.auth.models import User
from .models import Student, Country, State, City, Hobby, Contact


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': True})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'required': True})
    )
    gender = forms.ChoiceField(
        choices=Student.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'required': True})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Phone Number', 'required': True})
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        empty_label="Select Country",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_country', 'required': True})
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.all(),
        empty_label="Select State",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_state', 'required': True})
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label="Select City",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city', 'required': True})
    )
    hobbies = forms.ModelMultipleChoiceField(
        queryset=Hobby.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email address is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        cleaned_phone = re.sub(r'[\s\-\+\(\)]', '', phone)
        if not cleaned_phone.isdigit() or len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
            raise forms.ValidationError("Please enter a valid phone number (7 to 15 digits).")
        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            if dob >= today:
                raise forms.ValidationError("Date of birth must be in the past.")
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 5:
                raise forms.ValidationError("Student must be at least 5 years old.")
        return dob

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check file size (max 2 MB)
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Profile image size cannot exceed 2 MB.")
            # Check extension
            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            if not avatar.name.lower().endswith(valid_extensions):
                raise forms.ValidationError("Only JPG, JPEG, PNG, and WEBP image formats are supported.")
        return avatar

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get('country')
        state = cleaned_data.get('state')
        city = cleaned_data.get('city')

        if country and state:
            if state.country != country:
                self.add_error('state', f"The state '{state.name}' does not belong to '{country.name}'.")

        if state and city:
            if city.state != state:
                self.add_error('city', f"The city '{city.name}' does not belong to state '{state.name}'.")

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'required': True,
            'id': 'id_login_email',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your password',
            'required': True,
            'id': 'id_login_password',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your registered email address', 'required': True})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        # We intentionally do NOT raise an error here if email doesn't exist
        # to avoid revealing registered emails. The view handles it silently.
        return email



class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password (min 6 characters)', 'required': True})
    )
    confirm_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password', 'required': True})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address', 'required': True}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject of enquiry', 'required': True}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your message or question...', 'required': True}),
        }
