from django import forms
from .models import urlonboard

class urlonboardform(forms.ModelForm):
    class Meta:
        model = urlonboard
        fields= ["ip", "username", "password","url","ownername","owneremail","ownerphno"]
