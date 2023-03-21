from django.db import models

# Create your models here.
'''
class executecommand(models.Model):
    ip=models.CharField(max_length=16,primary_key=True)
    username=models.CharField(max_length=15)
    password=models.CharField(max_length=255)
'''

class portdetails(models.Model):
    ip=models.CharField(max_length=16,primary_key=True)
    username=models.CharField(max_length=15)
    password=models.CharField(max_length=255)
    port = models.CharField(max_length=5)

    def as_json(self):
        return dict(ip=self.ip,username=self.username,password=self.password,port=self.port)

class responsecommand(models.Model):
    statuscode=models.CharField(max_length=8, default='True')
    message=models.CharField(max_length=255, default='True')
    output=models.CharField(max_length=255, default='True')

class filesystemdetails(models.Model):
    filesystem = models.CharField(max_length=255, default='True')
    size = models.CharField(max_length=255, default='True')
    used = models.CharField(max_length=255, default='True')
    avail = models.CharField(max_length=255, default='True')
    use = models.CharField(max_length=255, default='True')
    mountpoint = models.CharField(max_length=255, default='True')

class onboardserver(models.Model):
    ip=models.CharField(max_length=16,primary_key=True)
    username=models.CharField(max_length=15)
    password=models.CharField(max_length=255)
    project=models.CharField(max_length=15, default='True')
    env=models.CharField(max_length=7, default='True')

class storedata(models.Model):
    ip=models.CharField(max_length=16,primary_key=True)
    project=models.CharField(max_length=15, default='True')
    env=models.CharField(max_length=7, default='True')
    usedspace=models.CharField(max_length=5, default='True')
    ram=models.CharField(max_length=5, default='True')
    swap=models.CharField(max_length=5, default='True')
    os=models.CharField(max_length=32, default='True')
    osversion=models.CharField(max_length=10, default='True')
    hostname=models.CharField(max_length=32)
    passwdauth=models.CharField(max_length=5, default='True')

class portmonitor(models.Model):
    ip=models.CharField(max_length=16)
    port=models.IntegerField()
    pid = models.CharField(max_length=8)
    status = models.CharField(max_length=5, default='DOWN')

class mountpoint(models.Model):
    filesystem = models.CharField(max_length=255)
    size = models.CharField(max_length=255)
    used = models.CharField(max_length=255)
    avail = models.CharField(max_length=255)
    use = models.CharField(max_length=255)
    mount = models.CharField(max_length=255)

    def as_json(self):
        return dict(
                filesystem =self.filesystem, size=self.size, used = self.used, avail = self.avail, use = self.use, mount = self.mount)

class applogfilesize(models.Model):
    filesize = models.CharField(max_length=255)
    path = models.CharField(max_length=255)

    def as_json(self):
        return dict(
                filesize = self.filesize, path = self.path)

class portinfo(models.Model):
    proto = models.CharField(max_length=255)
    recv =  models.CharField(max_length=2)
    send =  models.CharField(max_length=2)
    laddress = models.CharField(max_length=32)
    faddress =  models.CharField(max_length=32)
    state = models.CharField(max_length=8)
    pid = models.CharField(max_length=50)

    def as_json(self):
        return dict(
                proto=self.proto, recv=self.recv,send=self.send,laddress=self.laddress,faddress=self.faddress,state=self.state,pid=self.pid)


class  Document(models.Model):
    ip = models.CharField(max_length=16)
    document = models.FileField(upload_to='documents/')
    filelocation = models.CharField(max_length=255,default='null')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class errorresponse(models.Model):
    message = models.CharField(max_length=255,default='null')
    def as_json(self):
        return dict(message = self.message)
