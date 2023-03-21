from django.db import models
import uuid
# Create your models here.
from django.core.validators import RegexValidator

class urlonboard(models.Model):
    id =models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False)
    ip=models.CharField(max_length=16)
    username=models.CharField(max_length=15)
    password=models.CharField(max_length=25)
    url = models.CharField(max_length=255)
    ownername = models.CharField(max_length=50)
    owneremail = models.CharField(max_length=50)
    ownerphno = models.CharField(max_length=10, default=0)
