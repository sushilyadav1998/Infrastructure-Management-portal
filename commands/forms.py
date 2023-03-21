from django import forms
from .models import  onboardserver, storedata, portmonitor, Document

'''
class executecommandform(forms.ModelForm):
    class Meta:
        model = executecommand
        fields= ["ip", "username", "password"]
'''
class onboardserverform(forms.ModelForm):
    class Meta:
        model = onboardserver
        fields =  ["ip", "username", "password","project","env"]

class storedataform(forms.ModelForm):
    class Meta:
        model = storedata
        fields =  ["ip","project","env","usedspace","ram","swap","os","osversion","hostname"]

class portmonitorform(forms.ModelForm):
    class Meta:
        model = portmonitor
        fields = '__all__'

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["ip","document","filelocation"]
