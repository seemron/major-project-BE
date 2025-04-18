from django import forms
from django.contrib.auth.models import User
from .models import RFIDCard,Ride



class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ["start_latitude", "start_longitude"]




class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class RFIDCardForm(forms.ModelForm):
    class Meta:
        model = RFIDCard
        fields = ['card_id', 'balance']
