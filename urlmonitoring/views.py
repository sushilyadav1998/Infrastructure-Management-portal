from django.shortcuts import render

# Create your views here.
import paramiko
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from detail.services import is_valid_ip
#from urlmonitoring.models import urlmonitoring
#from urlmonitoring.forms import urlmonitoringform


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
        '''
        form = urlmonitoringform(urlonboarddetails)
        if form.is_valid():
            form.save(commit=True)
            return JsonResponse({'message':'URL Added Successfully'}, status=200, safe=False)
        '''
    else:
        return JsonResponse({'message': 'Only POST method is supported'}, status=404)

