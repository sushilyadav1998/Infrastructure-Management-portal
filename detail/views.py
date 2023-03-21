from django.shortcuts import render
#from jumpssh import SSHSession
import paramiko
import logging
import json
import shutil
#import ipaddress
#from ipaddress import ip_network
import requests
#from netaddr import IPNetwork 
import os
# django dependencies.
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from rest_framework.response import Response
from django.conf import settings
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import JSONParser

#models and serializers
from detail.serializers  import serverinfoSerializer, FileSerializer, basicinfoSerializer
from detail.models import serverinfo, File, basicinfo
from detail.services import validateip, is_valid_ip, validate, initializevalues
#from awx.api.info.serializers  import serverinfoSerializer, FileSerializer
#from awx.api.info.models import serverinfo, File
#from awx.api.info.services import validateip, is_valid_ip, validate, initializevalues

#logging
logging.basicConfig(filename="serverdetail.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

#Creating an object
logger=logging.getLogger()

class FileUploadView(APIView):
     parser_class = (FileUploadParser,)
     def post(self, request, *args, **kwargs):
         file_serializer = FileSerializer(data=request.data)
         f=request.data['file']
         print(f.name)
         print(f.content_type)
         if f.content_type != 'text/yaml':
             return JsonResponse({'message':'It supports yaml files only'}, status = 400, safe=False)
         mydict = dict(request.data)
         print(type(mydict))
         name = str(mydict.get("name"))
         filename = str(mydict.get("file"))
         print(filename)
         print(type(filename))
         name = name.strip('\[]')
         name = name.strip('\'')
         print(name)
         if name == '':
             return JsonResponse({'message':'Project directory should not be empty'}, status = 400, safe=False)
         if os.path.exists(settings.PROJECTS_ROOT):
             project=[]
             for x in os.listdir(settings.PROJECTS_ROOT):
                 project.append(x)
             if name in project:
                 settings.MEDIA_ROOT=os.path.join(settings.PROJECTS_ROOT, name)
                 print(settings.MEDIA_ROOT)
                 project=[]
                 for x in os.listdir(settings.MEDIA_ROOT):
                     project.append(x)
                 if f.name in project:
                     return JsonResponse({'message':'yaml file already exists in this path'}, status = 400, safe=False)
             else:
                 return JsonResponse({'message':'Project directory doesnot exist'}, status = 400, safe=False)
         if file_serializer.is_valid():
             file_serializer.save()
             return Response(file_serializer.data, status=status.HTTP_201_CREATED)
         else:
             return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)
@csrf_exempt
def project_list(request):
    print(request.method)
    if request.method == 'POST':
        requestbody = json.loads(request.body)
        name = requestbody.get('name')
        validate = str(name.isalnum())
        if validate == 'False':
            return JsonResponse({'message':'Project directory should not be extra charecters'}, status = 400, safe=False)
        if name == '':
            return JsonResponse({'message':'Project directory should not be empty'}, status = 400, safe=False)
        if os.path.exists(settings.PROJECTS_ROOT):
            project=[]
            for x in os.listdir(settings.PROJECTS_ROOT):
                project.append(x)
            if name in project:
                return JsonResponse({'message':'Project alredy present'}, status = 400, safe=False)
            else:
                newproject =os.path.join(settings.PROJECTS_ROOT, name)
                os.mkdir(newproject)
                return JsonResponse({'message':'New project created'}, status=200, safe=False)
        else:
            return JsonResponse({'message':'Project Root not available'}, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def delete_projectdirectory(request):
    if request.method == 'POST':
        requestbody = json.loads(request.body)
        name = requestbody.get('name')
        if name == '':
            return JsonResponse({'message':'Project directory should not be empty'}, status = 400, safe=False)
        if os.path.exists(settings.PROJECTS_ROOT):
            project=[]
            for x in os.listdir(settings.PROJECTS_ROOT):
                project.append(x)
            if name in project:
                deleteproject = os.path.join(settings.PROJECTS_ROOT, name)
                shutil.rmtree(deleteproject)
                return JsonResponse({'message':'Project successfully deleted'}, status=200, safe=False)
            else:
                return JsonResponse({'message':'Project directory doesnot present'}, status = 400, safe=False)
        else:
            return JsonResponse({'message':'Project Root not available'}, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def list_projectdirectory(request):
    if request.method == 'GET':
        if os.path.exists(settings.PROJECTS_ROOT):
            project = []
            for x in os.listdir(settings.PROJECTS_ROOT):
                project.append(x)
            output = {"data": project}
            return JsonResponse(output, status=200, safe=False)
        else:
             return JsonResponse({'message':'Project Root not available'}, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def detail_list(request):
    if request.method == 'POST':
        details = json.loads(request.body)
        print(type(details))
        serializer = basicinfoSerializer(data=details)
        if serializer.is_valid():
            serializer.save()
        details = json.loads(request.body)
        ip=details.get('ip')
        #initialzing the default values
        arr=[]
        initializevalues(ip)
        #validate username
        username = details.get('username')
        if username == '':
            serverinfo.statuscode = "400"
            serverinfo.message = "username should not be empty"
            output = validate(serverinfo)
            return JsonResponse(output, status=200, safe=False)
        #validate password
        password = details.get('password')
        if password == '':
            serverinfo.statuscode = "400"
            serverinfo.message = "password should not be empty"
            output = validate(serverinfo)
            return JsonResponse(output, status=200, safe=False)
        #validate IP
        if ip == '':
            serverinfo.statuscode = "400"
            serverinfo.message = "IP should not be empty"
            output = validate(serverinfo)
            logger.info("ip is empty")
            return JsonResponse(output, status=200, safe=False)
        else:
            ip=str(ip)
            res=str(ip.find('/'))
            if res == "-1":
                message = is_valid_ip(ip)
                if message != "success":
                    serverinfo.statuscode = "400"
                    serverinfo.message = "Invalid IP"
                    output = validate(serverinfo)
                    return JsonResponse(output, status=200, safe=False)
                data = JSONParser().parse(request)
                serializer = basicinfoSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                serverdetail = getinfo(ip,username,password)
                serverdetaildict = model_to_dict(serverdetail)
                print(type(serverdetaildict))
                serializerdict = serverinfoSerializer(data=serverdetaildict)
                if serializerdict.is_valid():
                    serializerdict.save()
                serializer = serverinfoSerializer(serverdetail).data
                arr.append(serializer)
                output = {"data": arr}
                return JsonResponse(output, status=200, safe=False)
            else:
                ip_list = validateip(ip)
                for x in ip_list:
                    ip = str(x)
                    serverdetail = getinfo(ip,username,password)
                    serializer = serverinfoSerializer(serverdetail).data
                    arr.append(serializer)
                    initializevalues(ip)
                output = {"data": arr}
                return JsonResponse(output, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

def getinfo(ip,username,password):
    IP = ip
    USER = username
    PASSWORD = password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    serverinfo.ip = IP
    try:
        #connection establishment
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="connection error"
        if(str(e) != "timed out"):
            e="Authentication Error"
        serverinfo.message = str(e)
        serverinfo.statuscode="400"
        logger.info("Exception raised when connecting to remote server and Exception is %s", e)
        ssh.close()
        return serverinfo
    #server ip
    logger.info("connected to remote server")
    ssh.exec_command("cd /tmp")
    #Getting Os information
    stdin,stdout,stderr = ssh.exec_command("cat /etc/os-release | grep '^NAME' | awk -F= '{print $2}'")
    outlines=stdout.readlines()
    os = ''.join(outlines)
    os = os.rstrip()
    serverinfo.os = os.strip('\"')

    #Getting Os version information
    stdin,stdout,stderr = ssh.exec_command("cat /etc/os-release | grep '^VERSION_ID' | awk -F= '{print $2}'")
    outlines = stdout.readlines()
    osversion=''.join(outlines)
    osversion = osversion.rstrip()
    serverinfo.osversion = osversion.strip('\"')

    #Getting Hostname of the Remote server 
    stdin,stdout,stderr = ssh.exec_command("hostname")
    outlines = stdout.readlines()
    hostname = ''.join(outlines)
    serverinfo.hostname = hostname.rstrip()
    serverinfo.message = "Success"
    serverinfo.url = "-"
    serverinfo.endpoint = "-"
    serverinfo.statuscode = "200"
    
    stdin,stdout,stderr = ssh.exec_command("dpkg -l | grep xroad-confproxy | awk '{print substr($2,0,20)}'")
    outlines = stdout.readlines()
    xroadcomponent = ''.join(outlines)
    xroadcomponent = xroadcomponent.rstrip()
    if xroadcomponent == 'xroad-confproxy':
        serverinfo.xroadcomponent = "jioroad-confproxy"
        stdin,stdout,stderr = ssh.exec_command("dpkg -l | grep xroad-confproxy | awk '{print substr($3,0,10)}'")
        outlines = stdout.readlines()
        xroadcomponentversion = ''.join(outlines)
        serverinfo.xroadcomponentversion = xroadcomponentversion.rstrip()

        return serverinfo

    #Getting security server information
    stdin,stdout,stderr = ssh.exec_command("dpkg -l | grep xroad-securityserver | awk '{print substr($2,0,20)}'")
    outlines = stdout.readlines()
    xroadcomponent = ''.join(outlines)
    xroadcomponent = xroadcomponent.rstrip()
    if xroadcomponent == 'xroad-securityserver':
        serverinfo.xroadcomponent = "jioroad-securityserver"
        stdin,stdout,stderr = ssh.exec_command("dpkg -l | grep xroad-securityserver | awk '{print substr($3,0,10)}'")
        outlines = stdout.readlines()
        xroadcomponentversion = ''.join(outlines)
        serverinfo.xroadcomponentversion = xroadcomponentversion.rstrip()
        stdin,stdout,stderr = ssh.exec_command("cat /etc/xroad/nginx/default-xroad.conf | grep listen |  awk '{print substr($2,0,5)}'")
        outlines = stdout.readlines()
        portnumber=''.join(outlines)
        portnumber=portnumber.strip('\n')
        if str(portnumber) == '':
            serverinfo.endpoint = "No end point found"
            serverinfo.url = "Failure"
            return serverinfo
        endpoint = "https://"+IP+":"+portnumber
        serverinfo.endpoint = endpoint
        serverinfo.url = "Success"
        logger.info("Remote server has security server installed %s", IP)
        return serverinfo
    
    #Getting central server information
    stdin,stdout,stderr = ssh.exec_command("dpkg -l | grep xroad-centralserver-monitoring | awk '{print substr($2,0,19)}'")
    outlines = stdout.readlines()
    xroadcomponent = ''.join(outlines)
    xroadcomponent = xroadcomponent.rstrip()
    if xroadcomponent == "xroad-centralserver":
        serverinfo.xroadcomponent = "jioroad-centralserver"
        stdin,stdout,stderr = ssh.exec_command("dpkg -l | grep xroad-centralserver-monitoring | awk '{print substr($3,0,10)}'")
        outlines = stdout.readlines()
        xroadcomponentversion = ''.join(outlines)
        serverinfo.xroadcomponentversion = xroadcomponentversion.rstrip()
        stdin,stdout,stderr = ssh.exec_command("cat /etc/xroad/nginx/default-xroad.conf | grep listen |  awk '{print substr($2,0,5)}'")
        outlines = stdout.readlines()
        portnumber=''.join(outlines)
        portnumber=portnumber.strip('\n')
        if str(portnumber) == '':
            serverinfo.endpoint = "No end point found"
            serverinfo.url = "Failure"
            return serverinfo
        endpoint = "https://"+IP+":"+portnumber
        serverinfo.endpoint = endpoint
        serverinfo.url = "Success"
        logger.info("Remote server has central server installed %s", IP)
        return serverinfo

    #If no Xroad component installed
    if (xroadcomponent != "xroad-securityserver" and xroadcomponent != "xroad-centralserver" and xroadcomponent != 'xroad-confproxy'):
        serverinfo.xroadcomponent = "No jioroad component installed"
        serverinfo.xroadcomponentversion = "-"
        logger.info("Remote server has no xroad component installed %s", IP)
        return serverinfo
    ssh.close()

    '''
    gateway_session = SSHSession('10.159.16.100','ubuntu',password='ubuntu').open()
    print("hello")
    remote_session = gateway_session.get_remote_session(IP,USER,password=PASSWORD)
    raise Exception('connection error')
    print('world')
    serverinfo.ip = IP
    #serverinfo.os= remote_session.get_cmd_output("hostnamectl | grep Operating | awk '{print substr($3,0,7)}'")
    remote_session.get_cmd_output("cd /tmp")
    print(remote_session.get_cmd_output("id $USER"))
    os= remote_session.get_cmd_output("cat /etc/os-release | grep '^NAME' | awk -F= '{print $2}'")
    serverinfo.os = os.strip('\"')
    #serverinfo.osversion= remote_session.get_cmd_output("hostnamectl | grep Operating | awk '{print substr($4,0,7)}'")
    osversion= remote_session.get_cmd_output("cat /etc/os-release | grep '^VERSION_ID' | awk -F= '{print $2}'")
    serverinfo.osversion=osversion.strip('\"')
    serverinfo.hostname=remote_session.get_cmd_output('hostname')

    xroadcomponent=remote_session.get_cmd_output("dpkg -l | grep xroad-securityserver | awk '{print substr($2,0,20)}'")
    if xroadcomponent == "xroad-securityserver":
        serverinfo.xroadcomponent=xroadcomponent
        serverinfo.xroadcomponentversion=remote_session.get_cmd_output("dpkg -l | grep xroad-securityserver | awk '{print substr($3,0,9)}'")
        return serverinfo

    xroadcomponent=remote_session.get_cmd_output("dpkg -l | grep xroad-centralserver-monitoring | awk '{print substr($2,0,19)}'")
    if xroadcomponent == "xroad-centralserver":
        serverinfo.xroadcomponent=xroadcomponent
        serverinfo.xroadcomponentversion=remote_session.get_cmd_output("dpkg -l | grep xroad-centralserver-monitoring | awk '{print substr($3,0,6)}'")
        return serverinfo

    if (xroadcomponent != "xroad-securityserver" and  xroadcomponent != "xroad-centralserver") :
        print("**********")
        serverinfo.xroadcomponent = "No xroad component installed"
        serverinfo.xroadcomponentversion="-"
        print(serverinfo.xroadcomponent)
        return serverinfo
    print(serverinfo)
    gateway_session.close()
'''
