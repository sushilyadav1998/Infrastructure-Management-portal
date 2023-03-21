from django.shortcuts import render

# Create your views here.
import paramiko
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from detail.services import is_valid_ip
from monitoring.models import urlonboard
from monitoring.forms import urlonboardform
import subprocess
from commands.models import responsecommand 

@csrf_exempt
def urlonboard_list(request):
    if request.method == 'POST':
        urlonboarddetails =  json.loads(request.body)
        username = urlonboarddetails.get('username')
        if username == '':
            return JsonResponse({'message':'username should not be empty'}, status=201, safe=False)
        password = urlonboarddetails.get('password')
        if password == '':
            return JsonResponse({'message':'password should not be empty'}, status=201, safe=False)
        ip = urlonboarddetails.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        url = urlonboarddetails.get('url')
        if url == '':
            return JsonResponse({'message':'URL should not be empty'}, status=201, safe=False)
        ownername = urlonboarddetails.get('ownername')
        if ownername == '':
            return JsonResponse({'message':'Owner should not be empty'}, status=201, safe=False)
        owneremail = urlonboarddetails.get('owneremail')
        if owneremail == '':
            return JsonResponse({'message':'Email should not be empty'}, status=201, safe=False)
        ownerphno = urlonboarddetails.get('ownerphno')
        if ownerphno == '':
            return JsonResponse({'message':'Phone Number should not be empty'}, status=201, safe=False)
        username = username.strip()
        password = password.strip()
        ip = ip.strip()
        url = url.strip()
        ownername = ownername.strip()
        owneremail = owneremail.strip()
        ownerphno = ownerphno.strip()
        message = is_valid_ip(ip)
        if message != "success":
            return JsonResponse({'message':'IP is Invalid'}, status=201, safe=False)
        print(ownername)
        form = urlonboardform(urlonboarddetails)
        print(form.errors)
        if form.is_valid():
            form.save(commit=True)
            return JsonResponse({'message':'URL Added Successfully'}, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only POST method is supported'}, status=404)

@csrf_exempt
def monitorurls_list(request):
    if request.method == 'GET':
        data = urlonboard.objects.values()
        for each in data:
            commanddetail = monitorurl(str(each['ip']),str(each['username']),str(each['password']),str(each['url']),str(each['owneremail']),str(each['ownerphno']))
        return JsonResponse({'message': 'Success'}, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

def monitorurl(ip,username,password,url,owneremail,ownerphno):
    IP = ip
    USER = username
    PASSWORD = password
    URL = '"'+url+'"'
    http = "HTTP/"
    http = '"'+http+'"' 
    print(URL)
    print(http)
    Email = owneremail
    Number = ownerphno
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="connection error"
        if(str(e) != "timed out"):
            e="Authentication Error"
        responsecommand.message = str(e)
        responsecommand.statuscode="400"
        responsecommand.output="-"
        ssh.close()
        return responsecommand
    command = "wget --spider -S "+URL+" 2>&1 | grep "+http+" | awk '{print $2}'"
    stdin,stdout,stderr = ssh.exec_command(command)
    outlines=stdout.readlines()
    statuscode = str(outlines[0])
    statuscode = statuscode.rstrip()
    if statuscode != '200':
        ssh1 = paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh1.connect(hostname="10.162.2.130",username="udeploy",password="clouduser@123",timeout=3)
        except Exception as e:
            if(str(e) == "timed out"):
                e="connection error"
            if(str(e) != "timed out"):
                e="Authentication Error"
            responsecommand.message = str(e)
            responsecommand.statuscode="400"
            responsecommand.output="-"
            ssh1.close()
            return responsecommand
        command = "sh /root/bash_scripts/ab.sh "+Email
        command = command+" "+url
        command = command+" "+statuscode
        command = command+" "+Number
        stdin,stdout,stderr = ssh1.exec_command("sh /root/bash_scripts/ab.sh "+Email+" "+url+" "+statuscode+" "+Number)
        outlines=stdout.readlines()
        print(outlines)
        return True
    return True
