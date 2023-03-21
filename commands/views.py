from django.shortcuts import render

# Create your views here.
from django.core import serializers
import paramiko
import json
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from commands.serializer import responsecommandSerializer, mountpointSerializer
from commands.models import portdetails, responsecommand, onboardserver, storedata, portmonitor, mountpoint, applogfilesize, portinfo, Document, errorresponse
from commands.forms import  onboardserverform, storedataform, portmonitorform, DocumentForm
from commands.models import mountpoint as mp
import re 
from django.forms.models import model_to_dict
from detail.services import is_valid_ip,validateip,validateserverdetails
import os
from django.conf import settings
import subprocess
from django.db.models import Q
from json import JSONEncoder
from scp import SCPClient
from threading import Thread
from django.db import connection

@csrf_exempt
def uploadfile_list(request):
    if request.method =='POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = Document()
            form.save()
            document.ip = form.cleaned_data["ip"]
            ip = document.ip
            print(request.FILES['document'].name)
            filename = request.FILES['document'].name
            filelocation = form.cleaned_data["filelocation"]
            transferfile(ip,filename,filelocation)
        return JsonResponse({'message':'Success'}, status=200, safe=False)
    else:
        return JsonResponse({'message':'Only Post Method supported'}, status=404, safe=False)

@csrf_exempt
def onboard_list(request):
    if request.method == 'POST':
        commanddetails = json.loads(request.body)
        username = commanddetails.get('username')
        if username == '':
            return JsonResponse({'message':'username should not be empty'}, status=201, safe=False)
        password = commanddetails.get('password')
        if password == '':
            return JsonResponse({'message':'password should not be empty'}, status=201, safe=False)
        ip = commanddetails.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        project = commanddetails.get('project')
        if project == '':
            return JsonResponse({'message':'Project Feild should not be empty'}, status=201, safe=False)
        env = commanddetails.get('env')
        if env == '':
            return JsonResponse({'message':'Environment Feild should not be empty'}, status=201, safe=False)
        username = username.strip()
        password = password.strip()
        ip = ip.strip()
        project = project.strip()
        env = env.strip()
        message = is_valid_ip(ip)
        if message != "success":
            return JsonResponse({'message':'IP is Invalid'}, status=201, safe=False)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=ip,username=username,password=password,timeout=3)
        except Exception as e:
            if(str(e) == "timed out"):
                e="connection error"
            if(str(e) != "timed out"):
                e="Authentication Error"
            return JsonResponse({'message':str(e)}, status=201, safe=False)
        stdin,stdout,stderr = ssh.exec_command("ls -l")
        outlines = stderr.readlines()
        if len(outlines) != 0:
            return JsonResponse({'message':'Please Enable Passwordless Sudo Access'}, status=201, safe=False)
        try:
            data = onboardserver.objects.get(ip=ip)
            return JsonResponse({'message':'Server Already Existed'}, status=201, safe=False)
        except Exception as e:
            form = onboardserverform(commanddetails)
            if form.is_valid():
                form.save(commit=True)
                getinfo(ip,username,password,project,env)
                return JsonResponse({'message':'Server Added Successfully'}, status=200, safe=False)
            else:
                return JsonResponse({'message':'Server Not Added Due To Missing Info'}, status=201, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)


@csrf_exempt
def updatecredentials_list(request):
    if request.method == 'POST':
        updatecredentials = json.loads(request.body)
        username = updatecredentials.get('username')
        if username == '':
            return JsonResponse({'message':'username should not be empty'}, status=201, safe=False)
        password = updatecredentials.get('password')
        if password == '':
            return JsonResponse({'message':'password should not be empty'}, status=201, safe=False)
        ip = updatecredentials.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        project = updatecredentials.get('project')
        if project == '':
            return JsonResponse({'message':'Project Feild should not be empty'}, status=201, safe=False)
        env = updatecredentials.get('env')
        if env == '':
            return JsonResponse({'message':'Environment Feild should not be empty'}, status=201, safe=False)
        username = username.strip()
        password = password.strip()
        ip = ip.strip()
        project = project.strip()
        env = env.strip()
        message = is_valid_ip(ip)
        if message != "success":
            return JsonResponse({'message':'IP is Invalid'}, status=201, safe=False)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=ip,username=username,password=password,timeout=3)
        except Exception as e:
            if(str(e) == "timed out"):
                e="connection error"
            if(str(e) != "timed out"):
                e="Authentication Error"
            return JsonResponse({'message':str(e)}, status=201, safe=False)
        stdin,stdout,stderr = ssh.exec_command("ls -l")
        outlines = stderr.readlines()
        if len(outlines) != 0:
            return JsonResponse({'message':'Please Enable Passwordless Sudo Access'}, status=201, safe=False)
        try:
            existdata = onboardserver.objects.get(ip=ip)
            existdata.env = env
            existdata.project = project
            existdata.username = username
            existdata.password = password
            existdata.save()
            getinfo(ip,username,password,project,env)
        except Exception as e:
            print(e)
        return JsonResponse({'message':'Details Updated Successfully'}, status=201, safe=False)
    else:
        return JsonResponse({'message': 'Only POST method is supported'}, status=404)
       
@csrf_exempt
def deleteonboardedserver_list(request):
    if request.method == 'DELETE':
        print(request.body)
        creddetails = json.loads(request.body)
        ip = creddetails.get('ip')
        print(ip)
        try:
            data = onboardserver.objects.get(ip=str(ip))
            data.delete()
        except Exception as e:
            message = str(e)
        try:
            data = storedata.objects.get(ip=str(ip))
            data.delete()
        except Exception as e:
            message = str(e)
        message = ip +" successfully Deleted"
        return JsonResponse({'message':message}, status = 200, safe=False)
    else:
        return JsonResponse({'message': 'Only Delete method is supported'}, status=404)

@csrf_exempt
def deletepid_list(request):
    if request.method == 'DELETE':
        piddata = json.loads(request.body)
        ip = piddata.get('ip')
        pid = piddata.get('pid')
        pid = re.findall(r"\d+",pid)
        pid = str(pid[0])
        command = "kill -9 "+pid
        print(pid)
        print(command)
        data = onboardserver.objects.filter(ip=str(ip))
        for each in data:
            commanddetail = executeanycommand(ip,str(each.username),str(each.password),command)
            print(commanddetail)
        print(str(pid))
        return JsonResponse({'message':'pid deleted'}, status = 200, safe=False)
    else:
        return JsonResponse({'message': 'Only Delete method is supported'}, status=404)

@csrf_exempt
def deletepath_list(request):
    if request.method == 'DELETE':
        pathdata = json.loads(request.body)
        ip= pathdata.get('ip')
        path = pathdata.get('path')
        print(path)
        command = "rm -rf "+path+"/*"
        print(command)
        data = onboardserver.objects.filter(ip=str(ip))
        for each in data:
            commanddetail = executeanycommand(ip,str(each.username),str(each.password),command)
            print(commanddetail)
        return JsonResponse({'message':'path deleted'}, status = 200, safe=False)
    else:
        return JsonResponse({'message': 'Only Delete method is supported'}, status=404)


@csrf_exempt
def runmultipletimes_list(request):
    if request.method == 'GET':
        data = onboardserver.objects.values()
        threads = []
        for each in data:
            print(str(each['ip']))
            #commanddetail = getinfo(str(each['ip']),str(each['username']),str(each['password']),str(each['project']),str(each['env']))
            
            t = Thread(target=getinfo, args=(str(each['ip']),str(each['username']),str(each['password']),str(each['project']),str(each['env']),))
            #commanddetail = getinfo(str(each['ip']),str(each['username']),str(each['password']),str(each['project']),str(each['env']))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return JsonResponse({'message': 'Success'}, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def managepassword_list(request):
    if request.method == 'GET':
        data = onboardserver.objects.values()
        threads = []
        for each in data:
            print(str(each['ip']))
            command = "chage -M 99999 "+str(each['username'])
            #executeanycommand(str(each['ip']),str(each['username']),str(each['password']),command)
            t = Thread(target=executeanycommand, args=(str(each['ip']),str(each['username']),str(each['password']),command,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return JsonResponse({'message': 'Success'}, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def servercredentials_list(request):
    if request.method == 'GET':
        data = onboardserver.objects.values()
        print(type(data))
        arr = []
        for each in data:
            data = {"ip":str(each['ip']),"project":str(each['project']),"env":str(each['env']),"username":str(each['username']),"password":str(each['password'])}
            arr.append(data)
        jsondata={"data":arr}
        return JsonResponse(jsondata, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def credentialprojectdata_list(request,projectname):
    if request.method == 'GET':
        data = onboardserver.objects.filter(project=str(projectname))
        if not data:
            return JsonResponse({'message': 'No Servers OnBoarded on this Project: '+projectname}, status=201)
        arr = []
        for each in data:
            data = {"ip":str(each.ip),"project":str(each.project),"env":str(each.env),"username":str(each.username),"password":str(each.password)}
            arr.append(data)
        jsondata={"data":arr}

        return JsonResponse(jsondata, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)


@csrf_exempt
def getdata_list(request):
    if request.method == 'GET':
        data = storedata.objects.values()
        arr = []
        for each in data:
            data = {"ip":str(each['ip']),"project":str(each['project']),"env":str(each['env']),"usedspace":str(each['usedspace']),"ram":str(each['ram']),"swap":str(each['swap']),"os":str(each['os']),"osversion":str(each['osversion']),"hostname":str(each['hostname'])}
            arr.append(data)
        jsondata={"data":arr}
        return JsonResponse(jsondata, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def projectdata_list(request,projectname):
    if request.method == 'GET':
        data = storedata.objects.filter(project=str(projectname))
        if not data:
            return JsonResponse({'message': 'No Servers OnBoarded on this Project: '+projectname}, status=201)
        arr = []
        for each in data:
            print(each.ip)    
            data = {"ip":str(each.ip),"project":str(each.project),"env":str(each.env),"usedspace":str(each.usedspace),"ram":str(each.ram),"swap":str(each.swap),"os":str(each.os),"osversion":str(each.osversion),"hostname":str(each.hostname)}
            arr.append(data)
        jsondata={"data":arr}
        
        return JsonResponse(jsondata, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def onboardportmonitoring(request):
    if request.method == 'POST':
        monitordetails = json.loads(request.body)
        ip = monitordetails.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        port = monitordetails.get('port')
        if port == '':
            return JsonResponse({'message':'PORT Number should not be empty'}, status=201, safe=False)
        message = is_valid_ip(ip)
        if message != "success":
            return JsonResponse({'message':'IP is Invalid'}, status=201, safe=False)
        data = portmonitor.objects.filter(Q(ip=str(ip)) & Q(port=str(port)))
        if data:
            return JsonResponse({'message': 'Monitoring For '+ip+' server on port '+port+' is enabled'}, status=201)
        data = onboardserver.objects.filter(ip=str(ip))
        if not data:
            return JsonResponse({'message': 'Please Onboard the server'}, status=201)
  
        for each in data:
            result = testport(ip,str(each.username),str(each.password),port)
        if result.message != '-':
            pid = result.message
            status = "UP"
            print(pid)
        else:
            pid = '-'
            status = "DOWN"
        data = {"ip":ip,"port":port,"status":status,"pid":pid}
        form = portmonitorform(data)
        print(form.errors)
        if form.is_valid():
            print(ip)
            form.save(commit=True)
        return JsonResponse({'message': 'Monitoring Started'}, status=200)

    else:
        return JsonResponse({'message': 'Only POST method is supported'}, status=404)

@csrf_exempt
def portmonitor_list(request):
    if request.method == 'GET':
        threads=[]
        arr = []
        data = portmonitor.objects.values()
        print(type(data))
        for each in data:
            ipdata = onboardserver.objects.filter(ip=str(each['ip']))
            for each1 in ipdata:
                pd = portdetails()
                pd.ip = str(each['ip'])
                pd.username=str(each1.username)
                pd.password=str(each1.password)
                pd.port=str(each['port'])
            arr.append(pd)

            #for each1 in ipdata:
                #commanddetail = testportupdate(str(each['ip']),str(each1.username),str(each1.password),str(each['port']))
   
   #             t = Thread(target=testport, args=(str(each['ip']),str(each1.username),str(each1.password),str(each['port']),))
            #commanddetail = getinfo(str(each['ip']),str(each['username']),str(each['password']),str(each['project']),str(each['env']))
      #          t.start()
    #            threads.append(t)
     #       for t in threads:
        #        t.join()
       #
   
        for data in arr:
            t = Thread(target=testportupdate, args=(str(data.ip),str(data.username),str(data.password),str(data.port),))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        
        return JsonResponse({'message': 'Success'}, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def projectportmonitor_list(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'Success'}, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def getportmonitor_list(request):
    if request.method == 'GET':
        data = portmonitor.objects.values()
        arr = []
        for each in data:
            data = {"ip":str(each['ip']),"port":str(each['port']),"pid":str(each['pid']),"status":str(each['status'])}
            print(each['ip'])
            print(each['port'])
            print(each['status'])
            print(each['pid'])
            arr.append(data)
        jsondata={"data":arr}
        return JsonResponse(jsondata, status=200)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)


@csrf_exempt
def command_list(request):
    if request.method == 'POST':
        commanddetails = json.loads(request.body)
        ip = commanddetails.get('ip')
        data = onboardserver.objects.filter(ip=str(ip))
        for each1 in data:
            commanddetail = getmountpoint(ip,str(each1.username),str(each1.password))
        data = {"data":commanddetail}
        return JsonResponse(data, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def applogdata_list(request,ip):
    if request.method == 'GET':
        data = onboardserver.objects.filter(ip=str(ip))
        for each in data:
            applogdata = getapplog(ip,str(each.username),str(each.password))
        data = {"data":applogdata}
        print(data)
        return JsonResponse(data, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def portlist(request,ip):
    if request.method == 'GET':
        data = onboardserver.objects.filter(ip=str(ip))
        for each in data:
            portlistdata = portlistmethod(ip,str(each.username),str(each.password))
        data = {"data":portlistdata}
        return JsonResponse(data, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only GET method is supported'}, status=404)

@csrf_exempt
def executecommand_list(request):
    if request.method == 'POST':
        commanddetails = json.loads(request.body)
        ip = commanddetails.get('ip')
        command = commanddetails.get('command')
        arr= []
        if (command == ''):
            return JsonResponse({'message': 'Command Feild Should Not be empty'}, status=201)
        data = onboardserver.objects.filter(ip=str(ip))
        for each in data:
            output = executeanycommand(ip,str(each.username),str(each.password),command)
            print(output)
            #dataset = {"ip":ip,"message" : commanddetail.output}
            #arr.append(dataset)
        if not output:
            data = {"output":'Success'}
            arr.append(data)
            data = {"data":arr}
            return JsonResponse(data, status=200)
        jsondata = json.loads(output)
        print(jsondata)
        for i in jsondata:
            data = {"output":i}
            arr.append(data)
        print(arr)
        data = {"data":arr}
        return JsonResponse(data, status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)


@csrf_exempt
def useradd_list(request):
    if request.method == 'POST':
        userdetails = json.loads(request.body)
        arr =[]
        message = validateserverdetails(userdetails)
        if message != 'Success':
            errmsg = message
            return JsonResponse({'message':errmsg}, status=400, safe=False)
        username = userdetails.get('username')
        username = username.strip()
        password = userdetails.get('password')
        password = password.strip()
        ip = userdetails.get('ip')
        ip = ip.strip()
        newusername = userdetails.get('newusername')
        if newusername == '':
            return JsonResponse({'message':'New username field should not be empty'}, status=400, safe=False)
        adduser = userdetails.get('adduser')
        if adduser == '':
            return JsonResponse({'message':'validater field should not be empty'}, status=400, safe=False)
        else:
            ip=str(ip)
            res=str(ip.find('/'))
            if res == "-1":
                message = is_valid_ip(ip)
                if message != "success":
                    return JsonResponse({'message':'IP is Invalid'}, status=400, safe=False)
                userdetail = useradd(ip,username,password,newusername,adduser)
                dataset = {"ip":ip,"message" : userdetail.output}
                arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
            else:
                ip_list = validateip(ip)
                for x in ip_list:
                    ip = str(x)
                    userdetail = useradd(ip,username,password,newusername,adduser)
                    dataset = {"ip":ip,"message":userdetail.output}
                    arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def telnet_list(request):
    if request.method == 'POST':
        telnetdetails = json.loads(request.body)
        arr =[]
        message = validateserverdetails(telnetdetails)
        if message != 'Success':
            errmsg = message
            return JsonResponse({'message':errmsg}, status=201, safe=False)
        username = telnetdetails.get('username')
        username = username.strip()
        password = telnetdetails.get('password')
        password = password.strip()
        ip = telnetdetails.get('ip')
        ip = ip.strip()
        remoteserver = telnetdetails.get('remoteserver')
        remoteserver = remoteserver.strip()
        if remoteserver == '':
            return JsonResponse({'message':'Remote server field should not be empty'}, status=201, safe=False)
        port = telnetdetails.get('port')
        port = port.strip()
        if port == '':
            return JsonResponse({'message':'Port field should not be empty'}, status=201, safe=False)
        else:
            ip=str(ip)
            res=str(ip.find('/'))
            if res == "-1":
                message = is_valid_ip(ip)
                if message != "success":
                    return JsonResponse({'message':ip+' is Invalid IP'}, status=201, safe=False)
                message = is_valid_ip(remoteserver)
                if message != "success":
                    return JsonResponse({'message':remoteserver+' is Invalid IP'}, status=201, safe=False)
                print("hello")
                telnetdetail = telnetserver(ip,username,password,remoteserver,port)
                dataset = {"ip":ip,"message" : telnetdetail.output}
                arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
            else:
                ip_list = validateip(ip)
                for x in ip_list:
                    ip = str(x)
                    telnetdetail = telnetserver(ip,username,password,remoteserver,port)
                    dataset = {"ip":ip,"message":telnetdetail.output}
                    arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def telnetonboardedserver_list(request):
    if request.method == 'POST':
        telnetdetail = json.loads(request.body)
        arr = []
        ip = telnetdetail.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        port = telnetdetail.get('port')
        if port == '':
            return JsonResponse({'message':'Port should not be empty'}, status=201, safe=False)
        remoteserver = telnetdetail.get('remoteserver')
        if remoteserver == '':
            return JsonResponse({'message':'Remote Server IP should not be empty'}, status=201, safe=False)
        data = onboardserver.objects.filter(ip=str(ip))
        if not data:
            return JsonResponse({'message': 'IP doesnot onboareded '+ip}, status=201)
        for each in data:
            telnetdetail = telnetserver(ip,str(each.username),str(each.password),remoteserver,port)
            dataset = {"ip":ip,"message" : telnetdetail.output}
            arr.append(dataset)
        output = {"data": arr}
        return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def portinfoonboardedserver_list(request):
    if request.method == 'POST':
        portinfodetail = json.loads(request.body)
        arr = []
        ip = portinfodetail.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        port = portinfodetail.get('port')
        if port == '':
            return JsonResponse({'message':'Port should not be empty'}, status=201, safe=False)
        data = onboardserver.objects.filter(ip=str(ip))
        if not data:
            return JsonResponse({'message': 'IP doesnot onboareded '+ip}, status=201)
        for each in data:
            telnetdetail = testport(ip,str(each.username),str(each.password),port)
            dataset = {"ip":ip,"message" : telnetdetail.output}
            arr.append(dataset)
        output = {"data": arr}
        return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def javainstall_list(request):
    if request.method =='POST':
        ipdetails = json.loads(request.body)
        ip = ipdetails.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        data = onboardserver.objects.filter(ip=str(ip))
        if not data:
            return JsonResponse({'message':'Please Onboard server'}, status=201, safe=False)
        for each in data:
            javaoutput = javainstall(ip,str(each.username),str(each.password))
            print(javaoutput)
        return JsonResponse({'message': 'Success'}, status=200)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)
     

@csrf_exempt
def port_info(request):
    if request.method == 'POST':
        portdetails = json.loads(request.body)
        username = portdetails.get('username')
        arr =[]
        if username == '':
            return JsonResponse({'message':'Username should not be empty'}, status=201, safe=False)
        password = portdetails.get('password')
        if password == '':
            return JsonResponse({'message':'Password should not be empty'}, status=201, safe=False)
        ip = portdetails.get('ip')
        if ip == '':
            return JsonResponse({'message':'IP should not be empty'}, status=201, safe=False)
        port = portdetails.get('port')
        if port == '':
            return JsonResponse({'message':'Port should not be empty'}, status=201, safe=False)
        else:
            ip=str(ip)
            res=str(ip.find('/'))
            if res == "-1":
                message = is_valid_ip(ip)
                if message != "success":
                    return JsonResponse({'message': ip+' is Invalid IP'}, status=201, safe=False)
                portdetail = testport(ip,username,password,port)
                dataset = {"ip":ip,"message":portdetail.output}
                arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
            else:
                ip_list = validateip(ip)
                for x in ip_list:
                    ip = str(x)
                    portdetail = testport(ip,username,password,port)
                    dataset = {"ip":ip,"message":portdetail.output}
                arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)


def transferfile(ip,filename,filelocation):
     ipdata = onboardserver.objects.filter(ip=str(ip))
     for each in ipdata:
         username = str(each.username)
         password = str(each.password)
     ssh = paramiko.SSHClient()
     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
     try:
         ssh.connect(hostname=ip,username=username,password=password,timeout=3)
     except Exception as e:
         if(str(e) == "timed out"):
             e="No Connectivity Between Host Server(10.159.18.32) to "+IP
         if(str(e) != "timed out"):
             e="Invalid Login Credentials of server "+IP
         ssh.close()
         responsecommand.message = str(e)
         responsecommand.statuscode="400"
         responsecommand.output= str(e)
         ssh.close()
         return responsecommand
   
     scp = SCPClient(ssh.get_transport())
     sourcepath = settings.MEDIA_ROOT+"/documents/"+filename
     destinationpath = "/tmp/"+filename
     scp.put(sourcepath,destinationpath)
     stdin,stdout,stderr = ssh.exec_command("sudo mv /tmp/"+filename+" "+filelocation)
     outlines=stdout.readlines()
     print(outlines)
     ssh.close()
     return True

def javainstall(ip,username,password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip,username=username,password=password,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
             e="No Connectivity Between Host Server(10.159.18.32) to "+ip
        if(str(e) != "timed out"):
             e="Invalid Login Credentials of server "+ip
       
        responsecommand.message = str(e)
        responsecommand.statuscode="400"
        responsecommand.output= str(e)
        ssh.close()
        return responsecommand
    scp = SCPClient(ssh.get_transport())
    sourcepath = "/root/javafiles/jdk-8u251-linux-x64.tar.gz"
    destinationpath = "/tmp/jdk-8u251-linux-x64.tar.gz"
    scp.put(sourcepath,destinationpath)
    stdin,stdout,stderr = ssh.exec_command("sudo  update-alternatives --remove java /app/jdk*/bin/java")
    outlines=stdout.readlines()
    print(outlines)
    stdin,stdout,stderr = ssh.exec_command("sudo  update-alternatives --remove java /opt/jdk*/bin/java")
    outlines=stdout.readlines()
    print(outlines)
    stdin,stdout,stderr = ssh.exec_command("sudo rm -rf /app/jdk*")
    outlines=stdout.readlines()
    print(outlines)
    stdin,stdout,stderr = ssh.exec_command("sudo rm -rf /opt/jdk*")
    outlines=stdout.readlines()
    print(outlines)
    stdin,stdout,stderr = ssh.exec_command("sudo tar -xvzf /tmp/jdk-8u251-linux-x64.tar.gz --directory /app/")
    outlines=stderr.readlines()
    print(outlines)

    stdin,stdout,stderr = ssh.exec_command("sudo update-alternatives --install /usr/bin/java java /app/jdk1.8.0_251/bin/java 2")
    outlines=stdout.readlines()
    print(outlines)

    stdin,stdout,stderr = ssh.exec_command("sudo update-alternatives --set java /app/jdk1.8.0_251/bin/java")
    outlines=stderr.readlines()
    print(outlines)
    return True
    '''
     ftp_client=ssh.open_sftp()
     sourcepath = "/root/testing/serverinfo/media/documents/"+filename
     print(sourcepath)
     destinationpath = "/tmp"+filename
     print(destinationpath)
     try:
         ftp_client.put(sourcepath,destinationpath,confirm=True)
     except Exception as e:
         print(e)
         if(str(e) == "timed out"):
             e="connection error"
         if(str(e) != "timed out"):
             e="Authentication Error"
         ssh.close()
         responsecommand.message = str(e)
         responsecommand.statuscode="400"
         responsecommand.output=str(e)
         ftp_client.close()
         return responsecommand
     stdin,stdout,stderr = ssh.exec_command("sudo mv /tmp/"+filename+" "+filelocation)
     outlines=stdout.readlines()
     print(outlines)
     return True
'''
def executeanycommand(ip,username,password,command):
    print(ip)
    print(command)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip,username=username,password=password,timeout=3)
    except Exception as e:
        print(e)
        if(str(e) == "timed out"):
            e="No Connectivity Between Host Server to "+IP
        if(str(e) != "timed out"):
            e="Invalid Login Credentials of server "+ip
        ssh.close()
        responsecommand.message = str(e)
        responsecommand.statuscode="400"
        responsecommand.output= str(e)
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo "+command)
    outlines=stdout.readlines()
    #print( outlines)
    #print("in outlines")
    arr = []
    if (outlines):
        for i in outlines:
            string = i.strip()
            string = string.strip('\"')
            arr.append(str(string))
        print(arr)
        return json.dumps(arr)
    err = stderr.readlines()
    print(err)
    if (err):
        for i in err:
            string = i.strip()
            string = string.strip('\"')
            arr.append(str(string))
        print(arr)
        ssh.close()
        return json.dumps(arr)
    
def telnetserver(ip,username,password,remoteserver,port):
    IP = ip
    USER = username
    PASSWORD = password
    REMOTESERVER = str(remoteserver)
    PORT = str(port)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="No Connectivity Between Host Server to "+IP
        if(str(e) != "timed out"):
            e="Invalid Login Credentials of server "+IP
        ssh.close()
        responsecommand.message = str(e)
        responsecommand.statuscode="400"
        responsecommand.output= str(e)
        ssh.close()
        return responsecommand      
    stdin,stdout,stderr = ssh.exec_command("echo 'exit' | telnet "+ REMOTESERVER +" "+PORT)
    outlines=stdout.readlines()
    errlines = stderr.readlines()
    if((len(errlines) != 0) and (len(outlines) == 0)):
        responsecommand.message = "user has no sudo accees on server"
        responsecommand.statuscode="200"
        responsecommand.output= str(errlines)
        ssh.close()
        return responsecommand
    print(outlines)
    if(len(outlines) == 1):
        print("HI")
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output= "Connection Refused from "+IP+" to "+REMOTESERVER+"  on the port "+PORT 
        ssh.close()
        return responsecommand
    else:
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output= "Connectivity is available from "+IP+" to "+REMOTESERVER+"  on the port "+PORT
        ssh.close()
        return responsecommand


def useradd(ip,username,password,newusername,adduser):
    IP = ip
    USER = username
    PASSWORD = password
    NEWUSERNAME = str(newusername)
    ADDUSER = str(adduser)
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
        responsecommand.message = str(e)
        responsecommand.statuscode="400"
        responsecommand.output="-"
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo id " + NEWUSERNAME)
    outlines=stdout.readlines()
    if ((len(outlines) == 0) and (ADDUSER == "TRUE")):
            stdin,stdout,stderr = ssh.exec_command( "sudo useradd " + NEWUSERNAME)
            outlines=stdout.readlines()
            responsecommand.output = "user added successfully"
            responsecommand.statuscode="200"
            responsecommand.message = "Success"
            ssh.close()
            return responsecommand
    if ((len(outlines) != 0) and (ADDUSER == "TRUE")):
        responsecommand.output = "user already existed"
        responsecommand.statuscode="200"
        responsecommand.message = "Success"
        ssh.close()
        return responsecommand
    if ((len(outlines) != 0) and(ADDUSER == "FALSE")):
        stdin,stdout,stderr = ssh.exec_command( "sudo userdel " + NEWUSERNAME)
        outlines=stdout.readlines()
        responsecommand.output = "user deleted successfully"
        responsecommand.statuscode="200"
        responsecommand.message = "Success"
        ssh.close()
        return responsecommand
    if ((len(outlines) == 0) and (ADDUSER == "FALSE")):
        responsecommand.output = "No user existed to delete"
        responsecommand.statuscode="200"
        responsecommand.message = "Success"
        ssh.close()
        return responsecommand
    else:
        responsecommand.output = "No proper inputs"
        responsecommand.statuscode="200"
        responsecommand.message = "Success"
        ssh.close()
        return responsecommand

def getmountpoint(ip,username,password):
    IP = ip
    USER = username
    PASSWORD = password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="No Connectivity Between Host Server to "+IP
        if(str(e) != "timed out"):
            e="Invalid Login Credentials of server "+IP
        ssh.close()
        responsecommand.message = str(e)
        responsecommand.statuscode="201"
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo df -h")
    outlines=stdout.readlines()
    arr=[]
    for each in outlines[1:]:
        res = [i for j in each.split() for i in (j, ' ')][:-1]
        mp = mountpoint()
        mp.filesystem=res[0]
        mp.size=res[2]
        mp.used=res[4]
        mp.avail=res[6]
        mp.use=res[8]
        mp.mount=res[10]
        print(mp.as_json())
        arr.append(mp.as_json())
    ssh.close()
    return arr


def portlistmethod(ip,username,password):
    IP = ip
    USER = username
    PASSWORD = password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="No Connectivity Between Host Server to "+IP
        if(str(e) != "timed out"):
            e="Invalid Login Credentials of server "+IP
        ssh.close()
        responsecommand.message = str(e)
        responsecommand.statuscode="201"
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp")
    outlines=stdout.readlines()
    print(outlines)
    outlines=outlines[2:]
    arr=[]
    for each in outlines:
        res = [i for j in each.split() for i in (j, ' ')]
        mp = portinfo()
        mp.proto=res[0]
        mp.recv=res[2]
        mp.send=res[4]
        mp.laddress=res[6]
        mp.faddress=res[8]
        mp.state=res[10]
        mp.pid=res[12]
        print(mp.as_json())
        arr.append(mp.as_json())
    ssh.close() 
    return arr

def getapplog(ip,username,password):
    IP = ip
    USER = username
    PASSWORD = password
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="No Connectivity Between Host Server to "+IP
        if(str(e) != "timed out"):
            e="Invalid Login Credentials of server "+IP
        ssh.close()
        responsecommand.message = str(e)
        responsecommand.statuscode="201"
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo du -h /app | sort -n -r | head -n 10")
    outlines=stdout.readlines()
    arr = []
    for each in outlines:
        res = [i for j in each.split() for i in (j, ' ')]
        applogfs = applogfilesize()
        applogfs.filesize = res[0]
        applogfs.path = res[2]
        arr.append(applogfs.as_json())
    a = {"app":arr}
    stdin,stdout,stderr = ssh.exec_command("sudo du -h /log | sort -n -r | head -n 10")
    outlines=stdout.readlines()
    arr = []
    for each in outlines:
        res = [i for j in each.split() for i in (j, ' ')]
        applogfs = applogfilesize()
        applogfs.filesize = res[0]
        applogfs.path = res[2]
        arr.append(applogfs.as_json())
    b = {"log":arr}
    c = {**a,**b}
    ssh.close()
    return c

def testport(ip,username,password,port):
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
            e="No Connectivity Between Host Server to "+IP
        if(str(e) != "timed out"):
            e="Invalid Login Credentials of server "+IP
        ssh.close()
        responsecommand.message = str(e)
        responsecommand.statuscode="201"
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp | grep -w " + PORT + " | awk '{print $7}'")

    outlines1=stdout.readlines()
    pid = ''.join(outlines1)
    pid = pid.rstrip()
    pid = re.findall(r"\d+",pid)
    if len(pid) == 0:
        responsecommand.output =  "No service is running on the port "+port+" on the server "+IP
        responsecommand.statuscode="200"
        responsecommand.message = "-"
        ssh.close()
        return responsecommand
    else:
        pid = str(pid[0])
        responsecommand.output = pid + " is the PID of the port "+port+" on the server "+IP
        responsecommand.statuscode="200"
        responsecommand.message = pid
        ssh.close()
        return responsecommand

def getinfo(ip,username,password,project,env):
    IP = ip
    USER = username
    PASSWORD = password
    PROJECT = project
    ENV = env
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=IP,username=USER,password=PASSWORD,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="connection error"
        if(str(e) != "timed out"):
            e="Authentication Error"
        try:
            print("Error at "+ip)
            existdata = storedata.objects.get(ip=IP)
            existdata.usedspace="-"
            existdata.ram="-"
            existdata.swap="-"
            existdata.os="Please Update Password"
            existdata.hostname="-"
            existdata.osversion="-"
            existdata.passwdauth="False"
            existdata.save()
        except:
            return True
        responsecommand.message = str(e)
        responsecommand.statuscode="400"
        responsecommand.output="-"
        ssh.close()
        return responsecommand
    #ssh.exec_command("cd /tmp")
    stdin,stdout,stderr = ssh.exec_command(" sudo free -h | awk 'NR == 3 {print $4}' ")
    outlines=stdout.readlines()
    err = stderr.readlines()
    if err:
        try:
            existdata = storedata.objects.get(ip=IP)
            print(ip +" error is"+err)
            existdata.project = PROJECT
            existdata.env = ENV
            existdata.usedspace = "" 
            existdata.ram=""
            existdata.swap=""
            existdata.os="Password Related Issue"
            existdata.osversion=""
            existdata.passwdauth="True"
            existdata.hostname=""
            existdata.save()
            return True
        except:
            return True
    swap = str(outlines[0])
    swap = swap.rstrip()

    stdin,stdout,stderr = ssh.exec_command("sudo df -h / |  awk 'NR == 2 {print $5}'")
    outlines=stdout.readlines()
    a = len(stderr.readlines())
    usedspace = str(outlines[0])
    usedspace=usedspace.rstrip()

    stdin,stdout,stderr = ssh.exec_command(" sudo free -h | awk 'NR == 2 {print $7}' ")
    outlines=stdout.readlines()
    b = len(stderr.readlines())
    ram = str(outlines[0])
    ram = ram.rstrip()

    stdin,stdout,stderr = ssh.exec_command("cat /etc/os-release | grep '^NAME' | awk -F= '{print $2}'")
    outlines=stdout.readlines()
    c = len(stderr.readlines())
    os = ''.join(outlines)
    os = os.rstrip()
    os = os.strip('\"')
    
    stdin,stdout,stderr = ssh.exec_command("cat /etc/os-release | grep '^VERSION_ID' | awk -F= '{print $2}'")
    outlines = stdout.readlines()
    d = len(stderr.readlines())
    osversion=''.join(outlines)
    osversion = osversion.rstrip()
    osversion = osversion.strip('\"')

    stdin,stdout,stderr = ssh.exec_command("hostname")
    outlines = stdout.readlines()
    hostname = ''.join(outlines)
    hostname = hostname.rstrip()
    print(hostname) 
    if ((a != 0) and (b != 0) and (c != 0) and (d != 0) and (e != 0)):
        os = "Password Related Issue"
        swap = ""
        usedspace = ""
        osversion =  ""
        ram = ""
        ip = IP
        project = PROJECT
        env = ENV
   
    data = {"ip":IP,"project":PROJECT,"env":ENV,"usedspace":usedspace,"ram":ram,"swap":swap,"os":os,"osversion":osversion,"hostname":hostname.lower(),"passwdauth":"True"}
    try:
        existdata = storedata.objects.get(ip=IP)
        existdata.project = PROJECT
        existdata.env = ENV
        existdata.usedspace = usedspace
        existdata.ram=ram
        existdata.swap=swap
        existdata.os=os
        existdata.osversion=osversion
        existdata.passwdauth="True"
        existdata.hostname=hostname.lower()
        existdata.save()
        connection.close()

        #existdata = storedata.objects.filter(Q(ip=str(ip))).update(usedspace=usedspace,ram=ram,swap=swap,passwdauth="True")
        #connection.close()
    except:
        form = storedataform(data)
        if form.is_valid():
            form.save(commit=True)
            connection.close()
    ssh.close()
    return True

def testportupdate(ip,username,password,port):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=ip,username=username,password=password,timeout=3)
    except Exception as e:
        if(str(e) == "timed out"):
            e="No Connectivity Between Host Server to "+ip
        if(str(e) != "timed out"):
            e="Invalid Login Credentials of server "+ip
        responsecommand.message = str(e)
        responsecommand.statuscode="201"
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp | grep -w " + port + " | awk '{print $7}'")
    outlines1=stdout.readlines()
    pid = ''.join(outlines1)
    pid = pid.rstrip()
    pid = re.findall(r"\d+",pid)
    print(ip)
    if len(pid) == 0:
        existdata = portmonitor.objects.filter(Q(ip=str(ip)) & Q(port=str(port))).update(pid="-",status="DOWN")
        connection.close()
        '''
        existdata.pid="-"
        existdata.status="DOWN"
        existdata.save()
        #connection.close()
        '''
        ssh.close()
        return True
    else:
        pid = str(pid[0])
        existdata = portmonitor.objects.filter(Q(ip=str(ip)) & Q(port=str(port))).update(pid=pid,status="UP")
        connection.close()
        '''
        existdata.pid="pid"
        existdata.status="UP"
        #connection.close()
        '''
        ssh.close()
        return responsecommand

