from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.forms.models import model_to_dict
from django.contrib.auth import logout
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
from django.template import engines

import urllib.request
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

from .models import Link


firebase_creds = credentials.Certificate(settings.FIREBASE_CONFIG)
firebase_app = firebase_admin.initialize_app(firebase_creds)


def iter_response(response, chunk_size=65536):
    try:
        while True:
            data = response.read(chunk_size)
            if not data:
                break
            yield data
    finally:
        response.close()

def catchall_dev(request, upstream='http://localhost:3000'):
    upstream_url = upstream + request.path
    response = urllib.request.urlopen(upstream_url)
    content_type = response.getheader('Content-Type')
    print('content type: ', content_type, '\n')

    if content_type == 'text/html; charset=utf-8':
        response_text = response.read().decode()
        response.close()
        return HttpResponse(
            engines['django'].from_string(response_text).render(),
            content_type=content_type,
            status=response.status,
            reason=response.reason,
        )
    else:
        return StreamingHttpResponse(
            iter_response(response),
            content_type=content_type,
            status=response.status,
            reason=response.reason,
        )

catchall_prod = TemplateView.as_view(template_name='index.html')
# catchall = catchall_dev if settings.DEBUG else catchall_prod
catchall = catchall_prod


def index(request):
    if request.method != "GET":
        return JsonResponse({"data":"Method not allowed"})
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing"})
    
    try:
        token = request.headers['Authorization']
        decoded_token = auth.verify_id_token(token)

        if decoded_token and decoded_token['user_id']:
            links = Link.objects.filter(user_id=decoded_token['user_id'])
            json_data = list(links.values())

            return JsonResponse(json_data, safe = False)
        else:
            return JsonResponse({"data": "Invalid Token"})
    except Exception as e:
        return JsonResponse({"data": str(e)})


def customLink(request, user_id, customUrl):
    if request.method != "GET":
        return JsonResponse({"data":"Method not allowed"})
    try:
        if user_id and customUrl:
            link = Link.objects.filter(customUrl=customUrl, user_id=user_id).first()
            if not link:
                return JsonResponse({"data": "Link does not exist"})
            response = link.response
            return JsonResponse({"data": response})
        else:
            return JsonResponse({"data": "user_id or customUrl is missing"})
        
    except Exception as e:
        return JsonResponse({"data": str(e)})


@csrf_exempt
def createLink(request):
    if request.method != "POST":
        return JsonResponse({"data":"Method not allowed"})
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = request.headers['Authorization']
        decoded_token = auth.verify_id_token(token)

        if decoded_token and decoded_token['user_id']:
            link = Link(customUrl=data['customUrl'], response=data['response'], user_id=decoded_token['user_id'])
            if not link:
                return JsonResponse({"data": "Error creating link"})
            
            link.save()
        else:
            return JsonResponse({"data": "Invalid Token"})
        return JsonResponse({"data": "Link Created"})
    except Exception as e:
        return JsonResponse({"data": str(e)})


@csrf_exempt
def editLink(request):
    if request.method != "POST":
        return JsonResponse({"data":"Method not allowed"})
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing"})

    try:
        data = json.loads(request.body.decode('utf-8'))
        token = request.headers['Authorization']
        decoded_token = auth.verify_id_token(token)

        if decoded_token and decoded_token['user_id']:
            link = Link.objects.filter(customUrl=data['customUrl'], user_id=decoded_token['user_id'])
            if not link:
                return JsonResponse({"data": "Link does not exist"})
            
            link.update(response=data['response'])
            return JsonResponse({"data": "Link updated"})
        else:
            return JsonResponse({"data": "Invalid Token"})
    except Exception as e:
        return JsonResponse({"data": str(e)})


@csrf_exempt
def deleteLink(request):
    if request.method != "POST":
        return JsonResponse({"data":"Method not allowed"})
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing"})
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = request.headers['Authorization']
        decoded_token = auth.verify_id_token(token)

        if decoded_token and decoded_token['user_id']:
            link = Link.objects.filter(customUrl=data['customUrl'], user_id=decoded_token['user_id']).first()
            if not link:
                return JsonResponse({"data": "Link does not exist"})
            
            link.delete()    
            return JsonResponse({"data": "Link deleted"})
        else:
            return JsonResponse({"data": "Invalid Token"})
    except Exception as e:
        return JsonResponse({"data": str(e)})
