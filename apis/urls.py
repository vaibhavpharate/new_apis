from django.urls import path, include

from .views import *
# v_wrf_alpha_file
urlpatterns = [
    path('admin_home', admin_home, name='admin-home'),
    path('admin_login', admin_login, name='admin-login'),
    path('create_client', create_client, name='create_client'),
    path('api_view/<str:token>',api_view_data,name='api-view'),
    path('api_view_site/<str:token>/<str:site_name>',api_view_site,name='api_view_site'),
    path('v_wrf_view/<str:token>',v_wrf_view,name='v-wrf-view'),
    path('v_wrf_alpha/<str:token>',v_wrf_view_alpha,name='v_wrf_alpha'),
    path('v_wrf_alpha_file/<str:token>/<str:file_name>',v_wrf_alpha_file,name='v_wrf_alpha_file'),
    path('v_wrf_site/<str:token>/<str:site_name>',v_wrf_view_alph_site,name='v_wrf_site')

]
