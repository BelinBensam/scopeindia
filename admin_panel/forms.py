from django import forms
from django.contrib.auth import authenticate
from main.models import (
    Course, Syllabus, Placement, FAQ, Country, State, City, Hobby, AboutContent
)


class AdminLoginForm(forms.Form):
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Staff Email or Username', 'required': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Staff Password', 'required': True})
    )

    def clean(self):
        cleaned_data = super().clean()
        login_val = cleaned_data.get('username_or_email', '').strip()
        pwd = cleaned_data.get('password')

        if login_val and pwd:
            user = authenticate(username=login_val, password=pwd)
            if not user and '@' in login_val:
                from django.contrib.auth.models import User
                try:
                    u = User.objects.get(email__iexact=login_val)
                    user = authenticate(username=u.username, password=pwd)
                except User.DoesNotExist:
                    user = None

            if not user:
                raise forms.ValidationError("Invalid staff credentials.")
            if not user.is_active:
                raise forms.ValidationError("This staff account is deactivated.")
            if not user.is_staff:
                raise forms.ValidationError("Access denied. You do not have staff/admin permissions.")

            self.user = user

        return cleaned_data


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'duration', 'fee', 'description', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python Full Stack Development'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 6 Months / 360 Hours'}),
            'fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Course Fee in INR'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Comprehensive course overview...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SyllabusForm(forms.ModelForm):
    class Meta:
        model = Syllabus
        fields = ['course', 'title', 'description', 'order']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Module 1: Python Basics & OOP'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Topics covered in this module...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class PlacementForm(forms.ModelForm):
    class Meta:
        model = Placement
        fields = ['image', 'name', 'company', 'role']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student Full Name'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hiring Company (e.g. TCS, Infosys)'}),
            'role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Role (e.g. Software Engineer)'}),
        }


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'order', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Frequently Asked Question'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed Answer...'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country Name'}),
        }


class StateForm(forms.ModelForm):
    class Meta:
        model = State
        fields = ['country', 'name']
        widgets = {
            'country': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State Name'}),
        }


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['state', 'name']
        widgets = {
            'state': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City Name'}),
        }


class HobbyForm(forms.ModelForm):
    class Meta:
        model = Hobby
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hobby / Tech Interest Name'}),
        }


class AboutContentForm(forms.ModelForm):
    class Meta:
        model = AboutContent
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Content body...'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
