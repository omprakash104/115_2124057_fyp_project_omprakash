from django import forms

class LoginView(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

from django import forms
from .models import *
from django.contrib.auth.models import User


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["ordered_by", "shipping_address",
                  "mobile", "email", "payment_method"]
        widgets = {
            "ordered_by": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Order By"
            }),
            "shipping_address": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your Shipping Address"
            }),
            "mobile": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your Mobile Number"
            }),
            "email": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your email"
            }),
            "payment_method": forms.Select(attrs={
                "class": "form-control"
                
            }),
            

        }

class AdminLoginView(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())


