from django.shortcuts import render

# Create your views here.

import paramiko
import json
import time
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from commands.serializer import responsecommandSerializer
from commands.models import responsecommand
import re
from django.forms.models import model_to_dict
from detail.services import is_valid_ip,validateip,validateserverdetails

@csrf_exempt
def swapstatus_list(request):
    if request.method == 'POST':
        swapdetails = json.loads(request.body)
        arr =[]
        message = validateserverdetails(swapdetails)
        if message != 'Success':
            errmsg = message
            return JsonResponse({'message':errmsg}, status=400, safe=False)
        username = swapdetails.get('username')
        password = swapdetails.get('password')
        ip = swapdetails.get('ip')
        operation = swapdetails.get('operation')
        if operation == '':
            return JsonResponse({'message':'Operation feild should not be empty'}, status=400, safe=False)
        else:
            ip=str(ip)
            res=str(ip.find('/'))
            if res == "-1":
                message = is_valid_ip(ip)
                if message != "success":
                    return JsonResponse({'message':'IP is Invalid'}, status=400, safe=False)
                swapdetail = swapstatus(ip,username,password,operation)
                dataset = {"ip":ip,"message" : swapdetail.output}
                arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
            else:
                ip_list = validateip(ip)
                for x in ip_list:
                    ip = str(x)
                    swapdetail = swapstatus(ip,username,password,operation)
                    dataset = {"ip":ip,"message":swapdetail.output}
                    arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

@csrf_exempt
def swapmonitor_list(request):
    if request.method == 'POST':
        swapdetails = json.loads(request.body)
        arr =[]
        print("HI")
        message = validateserverdetails(swapdetails)
        if message != 'Success':
            errmsg = message
            return JsonResponse({'message':errmsg}, status=400, safe=False)
        username = swapdetails.get('username')
        password = swapdetails.get('password')
        ip = swapdetails.get('ip')
        ip=str(ip)
        res=str(ip.find('/'))
        if res == "-1":
            message = is_valid_ip(ip)
            if message != "success":
                return JsonResponse({'message':'IP is Invalid'}, status=400, safe=False)
            swapdetail = swapmonitordetails(ip,username,password)
            dataset = {"ip":ip,"message" : swapdetail.output}
            arr.append(dataset)
            output = {"data": arr}
            return JsonResponse(output , status=200, safe=False)
        else:
            ip_list = validateip(ip)
            for x in ip_list:
                ip = str(x)
                swapdetail = swapmonitordetails(ip,username,password)
                dataset = {"ip":ip,"message":swapdetail.output}
                arr.append(dataset)
            output = {"data": arr}
            return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

def swapmonitordetails(ip,username,password):
    IP = ip
    USER = username
    PASSWORD = password
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
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    stdin,stdout,stderr = ssh.exec_command("sudo free -h | awk 'NR == 3 {print $2}'")
    totalsize = stdout.readlines()
    totalsize = str(totalsize[0]) 
    totalsize = totalsize.strip('\n')
    stdin,stdout,stderr = ssh.exec_command("sudo free -h | awk 'NR == 3 {print $3}'")
    occupiedsize = stdout.readlines()
    occupiedsize  = str(occupiedsize[0])
    occupiedsize = occupiedsize.rstrip()
    
    stdin,stdout,stderr = ssh.exec_command("sudo free -h | awk 'NR == 3 {print $4}'")
    freespace = stdout.readlines()
    freespace = str(freespace[0])
    freespace = freespace.strip('\n')
    responsecommand.message = '-'
    responsecommand.statuscode="400"
    responsecommand.output= "Total space is "+totalsize+"free space is "+freespace+" occupied space is "+occupiedsize+ "."
    ssh.close()
    return responsecommand
        
@csrf_exempt
def swapcreate_list(request):
    if request.method == 'POST':
        swapcreatedetails = json.loads(request.body)
        arr =[]
        message = validateserverdetails(swapcreatedetails)
        if message != 'Success':
            errmsg = message
            return JsonResponse({'message':errmsg}, status=400, safe=False)
        username = swapcreatedetails.get('username')
        password = swapcreatedetails.get('password')
        ip = swapcreatedetails.get('ip')
        swapsize = swapcreatedetails.get('swapsize')
        if swapsize == '':
            return JsonResponse({'message':'swapsize should not be empty'}, status=400, safe=False)
        try:
            swapsize = int(swapsize)
            if swapsize <= 0:
                return JsonResponse({'message':'swapsize should be greater than zero'}, status=400, safe=False)
        except ValueError:
            return JsonResponse({'message':'swapsize should be positive integer'}, status=400, safe=False)
        else:
            ip=str(ip)
            res=str(ip.find('/'))
            if res == "-1":
                message = is_valid_ip(ip)
                if message != "success":
                    return JsonResponse({'message':'IP is Invalid'}, status=400, safe=False)
                swapdetail = createswap(ip,username,password,swapsize)
                dataset = {"ip":ip,"message" : swapdetail.output}
                arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
            else:
                ip_list = validateip(ip)
                for x in ip_list:
                    ip = str(x)
                    swapdetail = createswap(ip,username,password,swapsize)
                    dataset = {"ip":ip,"message":swapdetail.output}
                    arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output , status=200, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

def createswap(ip,username,password,swapsize):
    IP = ip
    USER = username
    PASSWORD = password
    swapsize = str(swapsize)
    print(swapsize)
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
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    f = open("/tmp/swap.sh", "w+")
    f.write("#!/bin/bash "+'\n'+'\n')
    f.write("touch /swapfile"+'\n')
    f.write("fallocate --length " + swapsize + "GiB /swapfile"+'\n')
    f.write("chmod 600 /swapfile"+'\n')
    f.write("mkswap /swapfile"+'\n')
    f.write("swapon /swapfile"+'\n')
    f.write("echo '/swapfile                                 swap                    swap    defaults        0 0' >> /etc/fstab"+'\n')
    f.write("swapon -s"+'\n')
    f.close()
    ftp_client=ssh.open_sftp()
    try:
        ftp_client.put("/tmp/swap.sh","/tmp/swap.sh",confirm=True)
    except Exception as e:
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
    stdin,stdout,stderr = ssh.exec_command("sudo chmod 777 /tmp/swap.sh ")
    outlines=stdout.readlines()
    print(outlines)
    if(len(outlines) == 0):
        stdin,stdout,stderr = ssh.exec_command("sudo sh /tmp/swap.sh")
        outlines=stdout.readlines()
        print(outlines)
    responsecommand.message = "-"
    responsecommand.statuscode="200"
    responsecommand.output="file create"
    ssh.close()
    return responsecommand

def swapstatus(ip,username,password,operation):
    IP = ip
    USER = username
    PASSWORD = password
    operation = str(operation)
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
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    print(operation)
    stdin,stdout,stderr = ssh.exec_command("cat /proc/swaps | awk 'NR==2 {printf $1}'")
    outlines=stdout.readlines()
    print(len(outlines))
    if((operation == "STATUS") and (len(outlines) == 1)):
            responsecommand.message = "Success"
            responsecommand.statuscode="200"
            responsecommand.output=" Swap file present"
            ssh.close()
            return responsecommand
    if((operation == "ON") and (len(outlines) == 0)):
        stdin,stdout,stderr = ssh.exec_command("sudo swapon -a")
        swaponoutput=stdout.readlines()
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output=" Swap turned  on successfully"
        ssh.close()
        return responsecommand
    if((operation == "ON") and (len(outlines) == 1)):
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output=" Swap is already running"
        ssh.close()
        return responsecommand
    if((operation == "OFF") and (len(outlines) == 1)):
        stdin,stdout,stderr = ssh.exec_command("sudo swapoff -a")
        swaponoutput=stdout.readlines()
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output=" Swap turned off successfully"
        ssh.close()
        return responsecommand
    if((operation == "OFF") and (len(outlines) == 0)):
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output=" Swap is not running at all"
        ssh.close()
        return responsecommand
    if((operation == "STATUS") and (len(outlines) == 0)):
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output=" Swap file is not present all"
        ssh.close()
        return responsecommand
    else:
        responsecommand.message = "Success"
        responsecommand.statuscode="200"
        responsecommand.output="Invalid Option"
        ssh.close()
        return responsecommand
