from django import forms
from datetime import date
import re
from main.models import Student, Country, State, City, Hobby


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': True})
    )
    hobbies = forms.ModelMultipleChoiceField(
        queryset=Hobby.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'gender', 'date_of_birth', 'phone', 'country', 'state', 'city', 'hobbies', 'avatar']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'country': forms.Select(attrs={'class': 'form-select', 'id': 'id_country', 'required': True}),
            'state': forms.Select(attrs={'class': 'form-select', 'id': 'id_state', 'required': True}),
            'city': forms.Select(attrs={'class': 'form-select', 'id': 'id_city', 'required': True}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate country/state/city properly if instance exists
        if self.instance and self.instance.pk:
            if self.instance.country:
                self.fields['state'].queryset = State.objects.filter(country=self.instance.country)
            if self.instance.state:
                self.fields['city'].queryset = City.objects.filter(state=self.instance.state)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        cleaned_phone = re.sub(r'[\s\-\+\(\)]', '', phone)
        if not cleaned_phone.isdigit() or len(cleaned_phone) < 7 or len(cleaned_phone) > 15:
            raise forms.ValidationError("Please enter a valid phone number (7 to 15 digits).")
        return phone

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Avatar image size must not exceed 2 MB.")
            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
            if not avatar.name.lower().endswith(valid_extensions):
                raise forms.ValidationError("Only JPG, JPEG, PNG, and WEBP images are allowed.")
        return avatar

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get('country')
        state = cleaned_data.get('state')
        city = cleaned_data.get('city')

        if country and state and state.country != country:
            self.add_error('state', f"State '{state.name}' does not belong to {country.name}.")

        if state and city and city.state != state:
            self.add_error('city', f"City '{city.name}' does not belong to state {state.name}.")

        return cleaned_data


class ChangePasswordForm(forms.Form):
    existing_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Current / Temporary Password',
            'required': True,
            'id': 'id_existing_password',
            'autocomplete': 'current-password',
        })
    )
    new_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password (min 6 characters)',
            'required': True,
            'id': 'id_new_password',
            'autocomplete': 'new-password',
        })
    )
    confirm_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password',
            'required': True,
            'id': 'id_confirm_password',
            'autocomplete': 'new-password',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_existing_password(self):
        existing = self.cleaned_data.get('existing_password')
        if not self.user.check_password(existing):
            raise forms.ValidationError("Current password entered is incorrect.")
        return existing

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "New password and confirmation do not match.")
        if p1 and self.user.check_password(p1):
            self.add_error('new_password', "New password cannot be the same as your current password.")
        return cleaned_data

