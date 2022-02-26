from django.urls import path, re_path
from .views import index, customLink, createLink, editLink, deleteLink

urlpatterns = [
    path('', index, name='index'),
    path('create/', createLink, name='createLink'),
    path('editLink/', editLink, name='editLink'),
    path('deleteLink/', deleteLink, name='deleteLink'),
    re_path(r'(?P<user_id>[-\w]+)/(?P<custom_url>.*?)/?$', customLink, name='customLink'),
]
