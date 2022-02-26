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
import re

from .models import Link


firebase_creds = credentials.Certificate(settings.FIREBASE_CONFIG)
firebase_app = firebase_admin.initialize_app(firebase_creds)


def return_decoded_token(AuthToken):
    try:
        decoded_token = auth.verify_id_token(AuthToken.split(' ')[1])
        return decoded_token
    except Exception as e:
        return JsonResponse({"data": str(e), 'status':'false'}, status=400)

def index(request):
    if request.method != "GET":
        return JsonResponse({"data":"Method not allowed", 'status':'false'}, status=405)
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing", 'status':'false'}, status=403)
    
    try:
        token = request.headers['Authorization']
        decoded_token = return_decoded_token(token)
        
        if decoded_token and decoded_token['user_id']:
            links = Link.objects.filter(user_id=decoded_token['user_id']).order_by('-id')
            json_data = list(links.values())
            return JsonResponse(json_data, safe = False)
        else:
            return JsonResponse({"data": "Invalid Token", 'status':'false'}, status=401)
    except Exception as e:
        return JsonResponse({"data": "Exception: " + str(e), 'status':'false'}, status=400)


def customLink(request, user_id, custom_url):
    print('custom_url: ', custom_url)

    if request.method != "GET":
        return JsonResponse({"data":"Method not allowed", 'status':'false'}, status=405)
    try:
        if user_id and custom_url:
            print('customUrl: ' + custom_url)
            link = Link.objects.filter(customUrl=custom_url, user_id=user_id).first()
            if not link:
                return JsonResponse({"data": "Link does not exist", 'status':'false'}, status=404)
            response = link.response
            return JsonResponse({"data": response})
        else:
            return JsonResponse({"data": "user_id or custom_url is missing", 'status':'false'}, status=400)
        
    except Exception as e:
        return JsonResponse({"data": str(e), 'status':'false'}, status=400)


@csrf_exempt
def createLink(request):
    if request.method != "POST":
        return JsonResponse({"data":"Method not allowed", 'status':'false'}, status=405)
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing", 'status':'false'}, status=403)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = request.headers['Authorization']
        decoded_token = return_decoded_token(token)

        if decoded_token and decoded_token['user_id']:
            customUrl = data['customUrl']
            # clean customUrl
            customUrl = customUrl.replace(" ", "").lower()
            # remove trailing and ending slashes
            customUrl = re.sub(r'^/+|/+$', '', customUrl)
            # remove invalid characters
            customUrl = re.sub(r'[^a-zA-Z0-9-_/]', '', customUrl)
            # remove duplicate slashes
            customUrl = re.sub(r'/+', '/', customUrl)

            # if customUrl is empty
            if not customUrl:
                return JsonResponse({"data": "customUrl is empty after removing all special characters", 'status':'false'}, status=400)

            link = Link.objects.filter(user_id=decoded_token['user_id'], customUrl=customUrl).first()
            if link:
                return JsonResponse({"data": f"Link {customUrl} already exists after removing all special characters", 'status':'false'}, status=400)
            else:
                link = Link.objects.create(user_id=decoded_token['user_id'], customUrl=customUrl, response=data['response'])
                if not link:
                    return JsonResponse({"data": "Error creating link", 'status':'false'}, status=400)

                return JsonResponse({"data": f"Link {customUrl} created after removing all special characters"})
        else:
            return JsonResponse({"data": "Invalid Token", 'status':'false'}, status=401)
        return JsonResponse({"data": "Link Created", 'status':'false'})
    except Exception as e:
        return JsonResponse({"data": "Exception: " + str(e), 'status':'false'}, status=400)


@csrf_exempt
def editLink(request):
    if request.method != "POST":
        return JsonResponse({"data":"Method not allowed", 'status':'false'}, status=405)
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing", 'status':'false'}, status=401)

    try:
        data = json.loads(request.body.decode('utf-8'))
        token = request.headers['Authorization']
        decoded_token = return_decoded_token(token)

        if decoded_token and decoded_token['user_id']:
            link = Link.objects.filter(customUrl=data['customUrl'], user_id=decoded_token['user_id'])
            if not link:
                return JsonResponse({"data": "Link does not exist", 'status':'false'}, status=404)
            
            link.update(response=data['response'])
            return JsonResponse({"data": "Link updated"})
        else:
            return JsonResponse({"data": "Invalid Token", 'status':'false'}, status=401)
    except Exception as e:
        return JsonResponse({"data": str(e), 'status':'false'}, status=400)


@csrf_exempt
def deleteLink(request):
    if request.method != "POST":
        return JsonResponse({"data":"Method not allowed", 'status':'false'}, status=405)
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing", 'status':'false'}, status=401)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        token = request.headers['Authorization']
        decoded_token = return_decoded_token(token)

        if decoded_token and decoded_token['user_id']:
            link = Link.objects.filter(customUrl=data['customUrl'], user_id=decoded_token['user_id']).first()
            if not link:
                return JsonResponse({"data": "Link does not exist", 'status':'false'}, status=404)
            
            link.delete()    
            return JsonResponse({"data": "Link deleted"})
        else:
            return JsonResponse({"data": "Invalid Token", 'status':'false'}, status=401)
    except Exception as e:
        return JsonResponse({"data": str(e), 'status':'false'}, status=400)
