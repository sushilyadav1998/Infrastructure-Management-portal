from django.shortcuts import render
from glob import iglob
import mimetypes
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str
import json
import time
import os.path
import pathlib
from django.conf import settings
import subprocess
from django.http import HttpResponse, JsonResponse
from wsgiref.util import FileWrapper
from commands.models import responsecommand
import paramiko
import re
import subprocess

# Create your views here.
@csrf_exempt
def jartoexec_list(request):
    if request.method=='POST':
        reqdetails=json.loads(request.body)
        jarpath=reqdetails.get('jarpath')
        propertiespath=reqdetails.get('propertiespath')
        mainpackagename=reqdetails.get('mainpackagename')
        mainpackagename = mainpackagename.lower()
        subpackagename=reqdetails.get('subpackagename')
        subpackagename = subpackagename.lower()
        packageversion=reqdetails.get('packageversion')
        portnumber=reqdetails.get('portnumber')
        javacommand=reqdetails.get('javacommand')
        deployonremoteserver=reqdetails.get("deployonremoteserver")
        '''
        if jarpath == '':
            return JsonResponse({'message':'jar file path should not be empty'}, status = 400, safe=False)
        if propertiespath == '':
            return JsonResponse({'message':'property file path should not be empty'}, status = 400, safe=False)
            '''
        if mainpackagename == '':
            return JsonResponse({'message':'Main package name should not be empty'}, status = 400, safe=False)
        if subpackagename == '':
            return JsonResponse({'message':'Sub package name should not be empty'}, status = 400, safe=False)
        if packageversion == '':
            return JsonResponse({'message':'Package version should not be empty'}, status = 400, safe=False)
        '''
        if portnumber == '':
            return JsonResponse({'message':'Port number should not be empty'}, status = 400, safe=False)
            
        if javacommand == '':
            return JsonResponse({'message':'Java command should not be empty'}, status = 400, safe=False) 
            '''
        temp = str(packageversion.isnumeric())
        if temp == 'False':
            return JsonResponse({'message':'Package version should be numeric value'}, status = 400, safe=False)
        '''
        if ((portnumber < '0') and (portnumber > '65535')):
            return JsonResponse({'message':'Port number is out of range'}, status = 400, safe=False)
            '''
        if os.path.exists(settings.SCRIPT_FOLDER):
            temp = os.path.isfile("/var/www/html/debs/"+subpackagename+"-"+packageversion+".deb")
            if(str(temp) == 'True'):
                return JsonResponse({'message':'File already exist'}, status = 400, safe=False)
            else:
               os.chdir(settings.GIT_FOLDER)
               env = reqdetails.get('env')
               env = env.title()
               print(portnumber)
               subprocess.Popen(['./AACORE.sh'])
               time.sleep(15)
               pth = "/root/gittest/AA_Core/build/libs/"
               os.chdir(pth)
               for root,dirs,files in os.walk("."):
                   for filename in files:
                       jarfilename = filename
               jarloc = "/app/"+mainpackagename+"/"+subpackagename+"/"+packageversion+"/"+jarfilename
               propfile = "/app/"+mainpackagename+"/"+subpackagename+"/"+packageversion+"/application.properties"
               javacommand1 = "java -jar "+javacommand+" -Dspring.config.location="+propfile+" "+jarloc 
               print(javacommand1)
               propertiespath = "/root/gittest/Scripts/AA_Core/"+env+"/application.properties"
               jarpath = pth+jarfilename
               print(jarpath)
               separator = "="
               keys = {}
               with open(propertiespath) as f:
                   for line in f:
                       if separator in line:
                           name, value = line.split(separator, 1)
                           keys[name.strip()] = value.strip()
               
               portnumber = keys['server.port']
               print(propertiespath)
               os.chdir(settings.SCRIPT_FOLDER)
               with open(subpackagename+".sh",'w')as filehandler:
                   filebuffer=["#!/bin/bash","",javacommand1]
                   filehandler.writelines("%s\n" % line for line in filebuffer)

               subprocess.Popen(['./mkexec.sh %s %s %s %s %s %s '%(mainpackagename,subpackagename,packageversion,portnumber,jarpath,propertiespath)],shell=True) 
            deployonremote = reqdetails.get('deployonremote')
            if (deployonremote == 'True'):
                ip = reqdetails.get('ip')
                if ip == '':
                    return JsonResponse({'message':'IP should not be empty'}, status = 400, safe=False)
                username = reqdetails.get('username')
                if username == '':
                    return JsonResponse({'message':'username should not be empty'},status = 400, safe=False)
                password = reqdetails.get('password')
                if password == '':
                    return JsonResponse({'message':'password should not be empty'},status = 400, safe=False)
                serverdeploystatus = serverdeploy(ip,username,password,portnumber,subpackagename,packageversion)
                arr = []
                rpmurl = "http://10.159.18.32/rpms/"+subpackagename+"-"+packageversion+".rpm"
                deburl = "http://10.159.18.32/debs/"+subpackagename+"-"+packageversion+".deb"
                dataset = {"ip":ip,"message" : serverdeploystatus.output,"rpmurl":rpmurl,"deburl":deburl}
                arr.append(dataset)
                output = {"data": arr}
                return JsonResponse(output, status=serverdeploystatus.statuscode, safe=False)
            else:
                rpmurl = "http://10.159.18.32/rpms/"+subpackagename+"-"+packageversion+".rpm"
                deburl = "http://10.159.18.32/debs/"+subpackagename+"-"+packageversion+".deb"
                return JsonResponse({'message':'success','rpmurl':rpmurl,'deburl':deburl}, status = 200, safe=False)
        else:
            return JsonResponse({'message':'Script Folder doesnot exist'}, status = 400, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)

def serverdeploy(ip,username,password,portnumber,subpackagename,packageversion):
    IP = ip
    USER = username
    PASSWORD = password
    PORT = portnumber
    print(PORT)
    SUBPACKAGE = subpackagename
    PACKAGEVERSION = packageversion
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
        print("Here is the error")
        responsecommand.message = str(e)
        responsecommand.statuscode="400"
        responsecommand.output=str(e)
        ssh.close()
        return responsecommand
    command = "java -version 2>&1 | awk -F[\"\.] -v OFS=. 'NR==1{print $2,$3}'"
    print(command)
    stdin,stdout,stderr = ssh.exec_command(command)
    commandoutput = stdout.readlines()
    print(commandoutput)
    if (len(commandoutput) != 0):
        responsecommand.output = "Java is not installed"
        responsecommand.statuscode='400'
        ssh.close()
        return responsecommand

    stdin,stdout,stderr = ssh.exec_command("cat /etc/os-release | grep '^NAME' | awk -F= '{print $2}'")
    outlines=stdout.readlines()
    os = ''.join(outlines)
    os = os.rstrip()
    os = os.strip('\"')
    
    if os == "Ubuntu":
        stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp | grep " + PORT + " | awk '{print $7}'")
        outlines1=stdout.readlines()
        print(outlines1)
        pid = ''.join(outlines1)
        pid = pid.rstrip()
        pid = re.findall(r"\d+",pid)
        if len(pid) == 0:
            responsecommand.output =  "No service is running on the port "+PORT
            responsecommand.statuscode="200"
            responsecommand.message = "Success"
            ftp_client=ssh.open_sftp()
            try:
                ftp_client.put("/root/scriptfolder/"+SUBPACKAGE+"-"+PACKAGEVERSION+".deb","/tmp/"+SUBPACKAGE+"-"+PACKAGEVERSION+".deb",confirm=True)
            except Exception as e:
                print(e)
                if(str(e) == "timed out"):
                    e="connection error"
                if(str(e) != "timed out"):
                    e="Authentication Error"
                ssh.close()
                print("error in transfer file")
                responsecommand.message = str(e)
                responsecommand.statuscode="400"
                responsecommand.output=str(e)
                ftp_client.close()
                return responsecommand
            stdin,stdout,stderr = ssh.exec_command("sudo dpkg -i /tmp/"+SUBPACKAGE+"-"+PACKAGEVERSION+".deb")
            outlines1=stdout.readlines()
            print(outlines)
            responsecommand.output = "successfully installed"
            responsecommand.statuscode="200"
            responsecommand.message = "Success"
            ssh.close()
            return responsecommand
            '''
            stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp | grep " + PORT + " | awk '{print $7}'")
            outlines1=stdout.readlines()
            pid = ''.join(outlines1)
            pid = pid.rstrip()
            pid1 = re.findall(r"\d+",pid)
            print(pid1)
            if len(pid1) == 0:
                responsecommand.output =  "Unknown error while installing"
                responsecommand.statuscode="200"
                responsecommand.message = "Success"
                ssh.close()
                return responsecommand
            else:
                pid = str(pid[0])
                responsecommand.output = "successfully installed and PID is "+pid1
                responsecommand.statuscode="200"
                responsecommand.message = "Success"
                ssh.close()
                return responsecommand
            '''
        else:
            pid = str(pid[0])
            responsecommand.output = pid + " is the PID of the port "+PORT
            responsecommand.statuscode="200"
            responsecommand.message = "Success"
            ssh.close()
            return responsecommand
    else:
        stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp | grep " + PORT + " | awk '{print $7}'")
        outlines1=stdout.readlines()
        pid = ''.join(outlines1)
        pid = pid.rstrip()
        pid = re.findall(r"\d+",pid)
        if len(pid) == 0:
            responsecommand.output =  "No service is running on the port "+PORT
            responsecommand.statuscode="200"
            responsecommand.message = "Success"
            ftp_client=ssh.open_sftp()
            try:
                ftp_client.put("/var/www/html/rpms/"+SUBPACKAGE+"-"+PACKAGEVERSION+".rpm","/tmp/"+SUBPACKAGE+"-"+PACKAGEVERSION+".rpm",confirm=True)
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
            stdin,stdout,stderr = ssh.exec_command("sudo rpm -ivh --force /tmp/"+SUBPACKAGE+"-"+PACKAGEVERSION+".rpm")
            outlines1=stdout.readlines()
            responsecommand.output =  "successfully installed"
            responsecommand.statuscode="200"
            responsecommand.message = "Success"
            ssh.close()
            return responsecommand

            '''
            print(outlines1)
            stdin,stdout,stderr = ssh.exec_command("sudo netstat -ntlp | grep " + PORT + " | awk '{print $7}'")
            outlines1=stdout.readlines()
            print(outlines1)
            pid = ''.join(outlines1)
            pid = pid.rstrip()
            pid1 = re.findall(r"\d+",pid)
            if len(pid1) == 0:
                responsecommand.output =  "Unknown error while installing"
                responsecommand.statuscode="200"
                responsecommand.message = "Success"
                ssh.close()
                return responsecommand
            else:
                pid = str(pid[0])
                responsecommand.output = "successfully installed and PID is "+pid1
                responsecommand.statuscode="200"
                responsecommand.message = "Success"
                ssh.close()
                return responsecommand
            '''
        else:
            pid = str(pid[0])
            responsecommand.output = pid + " is the PID of the port "+PORT
            responsecommand.statuscode="200"
            responsecommand.message = "Success"
            ssh.close()
            return responsecommand
