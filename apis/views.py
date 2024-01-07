from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.http import JsonResponse, HttpResponse

# Rest Frameworks
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import renderers
from rest_framework.decorators import *

# Import Date Processors
import datetime as dtt
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Randomness
import string
import random

# Import User Forms
from django.contrib.auth.forms import AuthenticationForm
from .forms import ClientsForm, SiteConfigForm, ClientPlansForm

# import models
from .models import Clients, SiteConfig, Plans, ClientPlans, UserTokens, VDbApi, VWrfData, VWrfRevision, SiteConfig1
from .serializers import ClientAllSerializer, VBADataSerializer, VWrfViewSerializer, VWrfRevisionSerializer


# Create your views here.
@csrf_protect
def admin_login(request):
    form = AuthenticationForm()
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("admin-home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    context = {'admin_form': form}
    return render(request, template_name='apis/admin_login.html', context=context)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser or u.role_type == 'ADMIN', login_url='403')
def admin_home(request):
    clients = Clients.objects.filter(role_type='CLIENT').prefetch_related('user_tokens')
    clients = ClientAllSerializer(clients, many=True).data
    # clients = pd.DataFrame.from_records(clients)
    # print(type(clients))
    plans = Plans.objects.all().values()
    site_configs = SiteConfig.objects.all().values()
    client_plans = ClientPlans.objects.all().values()
    
    # client_sample_name = "Kreate"
    # gte = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")
    # client_sites_sample = list(SiteConfig.objects.filter(client_name=client_sample_name).values_list('site_name',flat=True))
    # v_wrf_revision = VWrfData.objects.filter(site_name__in=client_sites_sample).filter(timestamp__gte=gte).values()
    # print(v_wrf_revision)
    # print(clients)

    context = {'clients': clients, 'sites': site_configs, 'plans': plans, 'client_plans': client_plans}
    return render(request=request, template_name='apis/admin_home.html', context=context)


@login_required(login_url='admin-login')
@user_passes_test(lambda u: u.is_superuser or u.role_type == 'ADMIN', login_url='403')
def create_client(request):
    form = ClientsForm()
    if request.method == "POST":
        form = ClientsForm(request.POST, request.FILES)
        plan_type = request.POST['plan_type']
        if form.is_valid():
            group_data = form.cleaned_data['role_type']
            user = form.save()
            # Save admins to admin group
            client_group = Group.objects.get(name='Client')
            admin_group = Group.objects.get(name='Admin')

            # add client to their respective plans
            plan_type_map = Plans.objects.filter(plan_type=plan_type).values('plan_type')
            token = None
            try:
                user_id = Clients.objects.filter(username=user.username).values('id')
                client_plan = ClientPlans(client_id_id=user_id, plan_id_id=plan_type_map)
                client_plan.save()

                # create User Tokens
                token_length = 30
                tkn = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase +
                                             string.digits, k=token_length))
                date_now = datetime.now()
                validity = 365  # days
                valid_till = date_now + timedelta(days=validity)
                user_token = UserTokens(client_id=user_id, valid_till=valid_till, user_token=tkn)
                user_token.save()
                token = tkn
            except Exception as e:
                print(e)
            if group_data == "CLIENT":
                user.groups.add(client_group)
            elif client_group == "ADMIN":
                user.groups.add(admin_group)
                list_perms = ['Can add user', 'Can change user', 'Can delete user', 'Can view user']
                for x in list_perms:
                    permission = Permission.objects.get(name=x)
                    user.user_permissions.add(permission)
            messages.success(request, "Client Successfully Added")
            messages.success(request, f"Client Added to {plan_type} Plan")
            messages.success(request, f"Client User Token {token}")
            return redirect('create_client')
        else:
            messages.warning(request, "There was an error in the Form")
    context = {'form': form}
    return render(request=request, template_name='apis/create_client.html', context=context)


def verify_token(token):
    send_query = {'message': None, 'client': None, 'plan': None, 'session_status': 'Invalid'}
    if len(token) == 0:
        send_query['message'] = 'No Token Provided'
    else:
        user_token = UserTokens.objects.filter(user_token=token).values('client_id')
        if user_token.count() == 0:
            send_query['message'] = "Token is Invalid"
        else:
            client_id = user_token[0]['client_id']
            client_name = Clients.objects.filter(id=client_id).values('username')
            plans = ClientPlans.objects.filter(client_id_id=client_id).values('plan_id_id')[0]['plan_id_id']
            send_query['message'] = "Token Authentication is Successful !!"
            send_query['client'] = client_name[0]['username']
            send_query['session_status'] = 'Valid'
            send_query['plan'] = plans
        return send_query


def basic(client):
    # ref_date = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
    ref_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
    api_date_start = ref_date + timedelta(days=1)
    api_date_end = ref_date + timedelta(days=3)
    site_names = list(SiteConfig.objects.filter(client_name=client).filter(site_status='Active').values_list('site_name', flat=True))

    # Getting the APIS data
    now_api = VDbApi.objects.filter(site_name__in=site_names,
                                    timestamp__gte=api_date_start,
                                    timestamp__lte=api_date_end).values()
    data_serialize = VBADataSerializer(now_api, many=True)
    js_data = JSONRenderer().render(data_serialize.data)
    # file_name = datetime.now().strftime('%Y-%m-%d')
    return data_serialize.data


def premium(client):
    # api_date_start = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
    api_date_start = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)

    api_date_end = api_date_start + timedelta(days=3)
    site_names = list(SiteConfig.objects.filter(client_name=client).filter(site_status='Active').values_list('site_name', flat=True))
    # Getting the APIS data
    now_api = VDbApi.objects.filter(site_name__in=site_names,
                                    timestamp__gte=api_date_start,
                                    timestamp__lte=api_date_end).values()
    data_serialize = VBADataSerializer(now_api, many=True)
    return data_serialize.data

@api_view(['GET'])
def api_view_data(request, token):
    token_verification = verify_token(token=token)
    message = token_verification['message']
    data = None
    if token_verification['session_status'] != "Valid":
        print("The Session is Invalid")
        print(f"{message}")
    else:

        client = token_verification['client']
        plan = token_verification['plan']

        if plan == 'Basic':
            data = basic(client)
            print(type(data))
        elif plan == 'Premium':
            data = premium(client)
    return Response(data)


@api_view(['GET'])
def api_view_site(request,token,site_name):
    token_verification = verify_token(token=token)
    message = token_verification['message']
    data = None
    if token_verification['session_status'] != "Valid":
        print("The Session is Invalid")
        print(f"{message}")
    else:
        client = token_verification['client']
        plan = token_verification['plan']
        if plan == 'Basic':
            # ref_date = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            ref_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_start = ref_date + timedelta(days=1)
            api_date_end = ref_date + timedelta(days=3)
        
        elif plan == 'Premium':
            # api_date_start = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_start = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_end = api_date_start + timedelta(days=3)
        site_names = list(SiteConfig.objects.filter(client_name=client).filter(site_status='Active').values_list('site_name', flat=True))
        if site_name not in site_names:
                return Response({'message':'Site Not available in Site List','site_list':site_names})
        now_api = VDbApi.objects.filter(site_name=site_name,
                                    timestamp__gte=api_date_start,
                                    timestamp__lte=api_date_end).values()
        data_serialize = VBADataSerializer(now_api, many=True)
    return Response(data_serialize.data)



@api_view(['GET'])
def v_wrf_view(request, token):
    token_verification = verify_token(token=token)
    message = token_verification['message']
    # data = None
    api_date_start = None
    api_date_end = None
    if token_verification['session_status'] != "Valid":
        print("The Session is Invalid")
        print(f"{message}")
    else:
        client = token_verification['client']
        plan = token_verification['plan']
        if plan == 'Basic':
            # ref_date = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            ref_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_start = ref_date + timedelta(days=1)
            api_date_end = ref_date + timedelta(days=3)
        
        elif plan == 'Premium':
            # api_date_start = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_start = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_end = api_date_start + timedelta(days=3)
        site_names = list(SiteConfig.objects.filter(client_name=client).filter(site_status='Active').values_list('site_name', flat=True))
      
        now_api = VWrfData.objects.filter(site_name__in=site_names,
                                    timestamp__gte=api_date_start,
                                    timestamp__lte=api_date_end).values()
        data_serialize = VWrfViewSerializer(now_api, many=True)
    return Response(data_serialize.data)


@api_view(['GET'])
def v_wrf_view_alpha(request,token):
    token_verification = verify_token(token=token)
    message = token_verification['message']
    # data = None
    api_date_start = None
    api_date_end = None
    if token_verification['session_status'] != "Valid":
        print("The Session is Invalid")
        print(f"{message}")
        return Response({'data':'Session is Invalid!S'})
    else:
        client = token_verification['client']
        plan = token_verification['plan']
        if plan == 'Premium' or client == 'Kreate':
            site_names = list(SiteConfig.objects.filter(client_name=client).filter(site_status='Active').values_list('site_name', flat=True))
            if client == "Kreate":
                site_names = list(SiteConfig1.objects.filter(client_name=client).filter(site_status='Active').values_list('site_name', flat=True))
            print(site_names)
            # api_date_start = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_start = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_end = api_date_start + timedelta(days=3)
            now_api = VWrfRevision.objects.filter(site_name__in=site_names,
                                                timestamp__gte=api_date_start,
                                                timestamp__lte=api_date_end).values()
            data_serialize = VWrfRevisionSerializer(now_api,many=True)
            return Response(data_serialize.data)
        else:
            print("This is a Premium Resource")
            return Response({'message':'This is a Premium Resource'})
    



@api_view(['GET'])
def v_wrf_view_alph_site(request,token,site_name):
    token_verification = verify_token(token=token)
    message = token_verification['message']
    # data = None
    api_date_start = None
    api_date_end = None
    if token_verification['session_status'] != "Valid":
        print("The Session is Invalid")
        print(f"{message}")
        return Response({'data':'Session is Invalid!S'})
    else:
        client = token_verification['client']
        plan = token_verification['plan']
        if plan == 'Premium' or client == "Kreate":
            site_names = list(SiteConfig.objects.filter(client_name=client).filter(site_status='Active').values_list('site_name', flat=True))
            if site_name not in site_names:
                return Response({'message':'Site Not available in Site List','site_list':site_names})
            # api_date_start = datetime.strptime(datetime.now().date().strftime("%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_start = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")+ timedelta(hours=5,minutes=30)
            api_date_end = api_date_start + timedelta(days=3)
            now_api = VWrfRevision.objects.filter(site_name = site_name,
                                                timestamp__gte=api_date_start,
                                                timestamp__lte=api_date_end).values()
            data_serialize = VWrfRevisionSerializer(now_api,many=True)
            return Response(data_serialize.data)
        else:
            return Response({'message':'This is a Premium Resource'})
