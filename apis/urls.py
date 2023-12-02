from django.urls import path, include

from .views import *

urlpatterns = [
    path('admin_home', admin_home, name='admin-home'),
    path('admin_login', admin_login, name='admin-login'),
    path('create_client', create_client, name='create_client'),
    path('api_view/<str:token>',api_view,name='api-view')

]
