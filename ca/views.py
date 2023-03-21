from django.shortcuts import render
from glob import iglob
import mimetypes
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
import re
import subprocess

@csrf_exempt
def ca_list(request):
    if request.method == 'POST':
        cadetails=json.loads(request.body)
        countryname=cadetails.get('country')
        cao=cadetails.get('cao')
        caou=cadetails.get('caou')
        cacn=cadetails.get('cacn')
        ocspo=cadetails.get('ocspo')
        ocspou=cadetails.get('ocspou')
        ocspcn=cadetails.get('ocspcn')
        tsao=cadetails.get('tsao')
        tsaou=cadetails.get('tsaou')
        tsacn=cadetails.get('tsacn')
        if countryname == '':
            return JsonResponse({'message':'Country Name Should Not Be Empty '}, status = 201, safe=False)
        if cao == '':
            return JsonResponse({'message':'CA Organization Field Should Not Be Empty '}, status = 201, safe=False)
        if caou == '':
            return JsonResponse({'message':'CA Organization Unit Field Should Not Be Empty '}, status = 201, safe=False)
        if cacn == '':
            return JsonResponse({'message':'CA Common Name Should Not Be Empty'}, status = 201, safe=False)
        if ocspo == '':
            return JsonResponse({'message':'OCSP Organization Field Should Not Be Empty '}, status = 201, safe=False)
        if ocspcn == '':
            return JsonResponse({'message':'OCSP Common Name Should Not Be Empty'}, status = 201, safe=False)
        if ocspou == '':
            return JsonResponse({'message':'OCSP Organization Unit Field Should Not Be Empty '}, status = 201, safe=False)
        if tsao == '':
            return JsonResponse({'message':'TSA Organization Field Should Not Be Empty '}, status = 201, safe=False)
        if tsaou == '':
            return JsonResponse({'message':'TSA Organization Unit Field Should Not Be Empty '}, status = 201, safe=False)
        if tsacn == '':
            return JsonResponse({'message':'TSA Common Name Should Not Be Empty'}, status = 201, safe=False)
        
        if os.path.exists(settings.CA_FOLDER):
            os.chdir(settings.CA_FOLDER)
            subprocess.Popen(['./init.sh %s %s %s %s %s %s %s %s %s %s '%(countryname,cao,caou,cacn,ocspo,ocspcn,ocspou,tsao,tsaou,tsacn)],shell=True)
            cafileurl =  "http://10.159.18.32/ca/ca.cert.pem"
            ocspfileurl = "http://10.159.18.32/ca/ocsp.cert.pem"
            tsafileurl = "http://10.159.18.32/ca/tsa.cert.pem"
            return JsonResponse({'message':'success','cafile':cafileurl,'ocsp':ocspfileurl,'tsafile':tsafileurl}, status = 200, safe=False)
        else:
            return JsonResponse({'message':'CA folder is missing'}, status = 201, safe=False)
    else:
        return JsonResponse({'message': 'Only Post method is supported'}, status=404)





