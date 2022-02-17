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
        return {"data": str(e)}

def index(request):
    if request.method != "GET":
        return JsonResponse({"data":"Method not allowed"})
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing"})
    
    try:
        token = request.headers['Authorization']
        decoded_token = return_decoded_token(token)
        
        if decoded_token and decoded_token['user_id']:
            links = Link.objects.filter(user_id=decoded_token['user_id']).order_by('-id')
            json_data = list(links.values())
            return JsonResponse(json_data, safe = False)
        else:
            return JsonResponse({"data": "Invalid Token"})
    except Exception as e:
        return JsonResponse({"data": "Exception: " + str(e)})


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
        decoded_token = return_decoded_token(token)

        if decoded_token and decoded_token['user_id']:
            customUrl = data['customUrl']
            # clean customUrl
            customUrl = customUrl.replace(" ", "")
            customUrl = customUrl.replace("/", "")
            customUrl = customUrl.lower()
            customUrl = re.sub('[\W\_]', '', customUrl)
            # if customUrl is empty
            if not customUrl:
                return JsonResponse({"data": "customUrl is empty after removing all special characters"})

            link = Link.objects.filter(user_id=decoded_token['user_id'], customUrl=customUrl).first()
            if link:
                return JsonResponse({"data": "Link already exists after removing all special characters"})
            else:
                link = Link.objects.create(user_id=decoded_token['user_id'], customUrl=customUrl, response=data['response'])
                if not link:
                    return JsonResponse({"data": "Error creating link"})

                return JsonResponse({"data": "Link created after removing all special characters"})
        else:
            return JsonResponse({"data": "Invalid Token"})
        return JsonResponse({"data": "Link Created"})
    except Exception as e:
        return JsonResponse({"data": "Exception: " + str(e)})


@csrf_exempt
def editLink(request):
    if request.method != "POST":
        return JsonResponse({"data":"Method not allowed"})
        
    if 'Authorization' not in request.headers:
        return JsonResponse({"data": "Authorization header is missing"})

    try:
        data = json.loads(request.body.decode('utf-8'))
        token = request.headers['Authorization']
        decoded_token = return_decoded_token(token)

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
        decoded_token = return_decoded_token(token)

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
