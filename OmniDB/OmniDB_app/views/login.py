from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.core import serializers
from django.shortcuts import redirect
from OmniDB import settings
import json

import sys

import OmniDB_app.include.Spartacus as Spartacus
import OmniDB_app.include.Spartacus.Database as Database
import OmniDB_app.include.Spartacus.Utils as Utils
import OmniDB_app.include.OmniDatabase as OmniDatabase
from OmniDB_app.include.Session import Session
from OmniDB import settings, custom_settings

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as logout_django

from OmniDB_app.models.main import *
from django.contrib.auth.models import User

import logging
logger = logging.getLogger(__name__)
print(logger)

def check_session(request):
    if not request.user.is_authenticated:
        return redirect('/omnidb_login')
    else:
        # User is authenticated, check if user details object exists.
        try:
            user_details = UserDetails.objects.get(user=request.user)
        # User details does not exist, create it.
        except Exception:
            user_details = UserDetails(user=request.user)
            user_details.save()

        #Invalid session
        if not request.session.get('omnidb_session'):
            print('creating')
            #creating session key to use it
            request.session.save()

            v_session = Session(
                request.user.id,
                request.user.username,
                'light',
                user_details.font_size,
                request.user.is_superuser,
                request.session.session_key,
                user_details.csv_encoding,
                user_details.csv_delimiter
            )

            request.session['omnidb_session'] = v_session

        return redirect('/workspace')

def index(request):
    context = {
        'omnidb_short_version': settings.OMNIDB_SHORT_VERSION,
        'url_folder': settings.PATH
    }

    user = request.GET.get('user', '')
    pwd = request.GET.get('pwd', '')

    if user and pwd:
        num_connections = sign_in_automatic(request,user,pwd)

        if num_connections >= 0:
            return redirect('workspace')
        else:
            return HttpResponse("INVALID APP TOKEN")

    template = loader.get_template('OmniDB_app/new_login.html')
    return HttpResponse(template.render(context, request))

def logout(request):

    v_session = request.session.get('omnidb_session')
    logger.info('User "{0}" logged out.'.format(v_session.v_user_name))
    logout_django(request)

    return redirect('/omnidb_login')

def check_session_message(request):

    v_return = {}
    v_return['v_data'] = ''
    v_return['v_error'] = False
    v_return['v_error_id'] = -1

    if request.session.get('omnidb_alert_message'):
        v_return['v_data'] = request.session.get('omnidb_alert_message')
        request.session['omnidb_alert_message'] = ''

    return JsonResponse(v_return)

def sign_in_automatic(request, username, pwd):

    token = request.GET.get('token', '')
    valid_token = custom_settings.APP_TOKEN

    if valid_token and token != valid_token:
        return -1

    database = OmniDatabase.Generic.InstantiateDatabase(
        'sqlite',
        '',
        '',
        settings.OMNIDB_DATABASE,
        '',
        '',
        '0',
        '',
        True
    )

    table = database.v_connection.Query('''
        select u.user_id,
               u.password,
               t.theme_id,
               t.theme_name,
               t.theme_type,
               u.editor_font_size,
               (case when u.chat_enabled is null then 1 else u.chat_enabled end) as chat_enabled,
               (case when u.super_user is null then 0 else u.super_user end) as super_user,
               u.csv_encoding,
               u.csv_delimiter,
               u.interface_font_size
        from users u,
             themes t
         where u.theme_id = t.theme_id
        and u.user_name = '{0}'
    '''.format(username))

    if len(table.Rows) > 0:
        cryptor = Utils.Cryptor('omnidb', 'iso-8859-1')

        if cryptor.Hash(cryptor.Encrypt(pwd)) == table.Rows[0]['password']:

            #creating session key to use it
            try:
                request.session.save()
            except Exception as exc:
                request.session.create()

            logger.info('User "{0}" logged in.'.format(username))

            v_session = Session(
                table.Rows[0]["user_id"],
                username,
                database,
                table.Rows[0]["theme_name"],
                table.Rows[0]["theme_type"],
                table.Rows[0]["theme_id"],
                table.Rows[0]["editor_font_size"],
                table.Rows[0]["interface_font_size"],
                int(table.Rows[0]["chat_enabled"]),
                int(table.Rows[0]["super_user"]),
                cryptor,
                request.session.session_key,
                table.Rows[0]["csv_encoding"],
                table.Rows[0]["csv_delimiter"]
            )

            #v_session.RefreshDatabaseList()
            request.session['omnidb_session'] = v_session

            if not request.session.get('cryptor'):
                request.session['cryptor'] = cryptor

            return len(v_session.v_databases)

    return -1

def create_user_session(request, user, user_details):
    #creating session key to use it
    request.session.save()

    v_session = Session(
        user.id,
        user.username,
        'light',
        user_details.font_size,
        request.user.is_superuser,
        request.session.session_key,
        user_details.csv_encoding,
        user_details.csv_delimiter
    )

    request.session['omnidb_session'] = v_session


def sign_in(request):
    v_return = {}
    v_return['v_data'] = -1
    v_return['v_error'] = False
    v_return['v_error_id'] = -1

    valid_token = custom_settings.APP_TOKEN

    if valid_token:
        v_return['v_data'] = -2
        return JsonResponse(v_return)

    json_object = json.loads(request.POST.get('data', None))
    username = json_object['p_username']
    pwd = json_object['p_pwd']

    user = authenticate(username=username, password=pwd)
    if user is not None:
        login(request, user)
    else:
        return JsonResponse(v_return)

    logger.info('User "{0}" logged in.'.format(username))

    v_return['v_data'] = 0

    return JsonResponse(v_return)
