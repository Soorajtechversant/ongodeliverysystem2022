from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django import forms
from burgerapp.models import  HotelName


class HotelForm(forms.ModelForm):
    class Meta:
        model = HotelName
        fields = "__all__"



class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(max_length=255, required=True)
    phone = forms.CharField(max_length=14, required=True)
    address = forms.EmailField(max_length=255, required=True)
    class Meta:
        model = UserDetails
        fields = ('username', 'email', 'phone' , 'address' ,  'password1', 'password2' )


class MerchantSignupForm(UserCreationForm):
    email = forms.EmailField(max_length=255, required=True)
    hotelname = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=12, required=True)
    businesstype = forms.CharField(max_length=255, required=True)
    address = forms.EmailField(max_length=255, required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'hotelname' , 'phone' , 'address' ,  'password1', 'password2' , 'businesstype')


