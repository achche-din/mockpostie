from django.urls import path
from .views import index, customLink, createLink, editLink, deleteLink


urlpatterns = [
    path('', index, name='index'),
    path('<slug:user_id>/<slug:customUrl>/', customLink, name='customLink'),
    path('create/', createLink, name='createLink'),
    path('editLink/', editLink, name='editLink'),
    path('deleteLink/', deleteLink, name='deleteLink'),
]
