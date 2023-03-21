from django.db import models
# Create your models here.

class serverinfo(models.Model):
    ip=models.CharField(max_length=16,primary_key=True)
    hostname=models.CharField(max_length=15)
    os=models.CharField(max_length=15)
    osversion=models.CharField(max_length=10)
    xroadcomponent=models.CharField(max_length=10)
    xroadcomponentversion=models.CharField(max_length=10)
    statuscode=models.CharField(max_length=8, default='True')
    message=models.CharField(max_length=255, default='True')
    url=models.CharField(max_length=255, default='True')
    endpoint=models.CharField(max_length=255, default='True')

class basicinfo(models.Model):
    ip=models.CharField(max_length=16,primary_key=True)
    username=models.CharField(max_length=15)
    password=models.CharField(max_length=255)

class File(models.Model):
    file = models.FileField(blank=False, null=False)
