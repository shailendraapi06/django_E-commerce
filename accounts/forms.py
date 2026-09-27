from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Accounts

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            user = Accounts(
                first_name=self.cleaned_data.get('first_name', ''),
                last_name=self.cleaned_data.get('last_name', ''),
                email=self.cleaned_data.get('email', ''),
            )
            validate_password(password, user)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data
