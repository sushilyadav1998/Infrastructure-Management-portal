from django.shortcuts import render

# Create your views here.
import paramiko
import json
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test_port(request):
    if request.method == 'POST':
        portdetails = json.loads(request.body)
        username = portdetails.get('username')
        if username == '':
            return JsonResponse({'message':'username should not be empty'}, status=400, safe=False)
        password = portdetails.get('password')
        if password == '':
            return JsonResponse({'message':'password should not be empty'}, status=400, safe=False)
        ip = portdetails.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=400, safe=False)
        port = portdetails.get('port')
        if port == '':
            return JsonResponse({'message':'port should not be empty'}, status=400, safe=False)
        else:
            commanddetail = getinfo(ip,username,password,port)
            return JsonResponse({'message': 'success'}, status=200)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

def getinfo(ip,username,password,port):
    IP = ip
    USER = username
    PASSWORD = password
    PORT = port
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="connection error"
        if(str(e) != "timed out"):
            e="Authentication Error"
        ssh.close()
        return False
    stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp | grep "+port)
    outlines=stdout.readlines()
    print(outlines)
    return True




    

