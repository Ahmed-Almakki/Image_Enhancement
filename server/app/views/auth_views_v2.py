from django.http import JsonResponse
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
import environ
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import json
from pathlib import Path
import requests
import secrets

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


def sendState(request):
    from urllib.parse import urlencode
    print(f'request {request}\n\n\n get {request.GET}')
    state = secrets.token_urlsafe(24)
    request.session['oauth_state'] = state
    params = {
        'state': state,
        'redirect_uri': env('REDIRECT_URI'),
        'client_id': env('CLIENT_ID'),
        'response_type': 'code',
        'scope': 'openid profile email',
        'access_type': 'offline',
        'prompt': 'consent'
    }
    google_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return JsonResponse({'status': True, 'data': google_url})


def loginRegister(request):
    try:
        # get the code and the state from the oauth
        code = request.GET.get('code')
        state = request.GET.get('state')

        # use the code to get the token
        data = {
            'code': code,
            'client_id': env('CLIENT_ID'),
            'client_secret': env('SECRET_KEY_OAUTH'),
            'redirect_uri': env('REDIRECT_URI'),
            'grant_type': 'authorization_code'
        }
        response = requests.post('https://oauth2.googleapis.com/token', data=data)

        # extract the information
        body = json.loads(response.content)
        token_id = body.get('id_token')
        refresh_token = body.get('refresh_token')
        access_token = body.get('access_token')

        id_info = id_token.verify_oauth2_token(
            token_id,
            google_requests.Request(),
            audience=env('CLIENT_ID')
        )
        google_id = id_info['sub']
        email = id_info['email']
        first_name = id_info['given_name']
        last_name = id_info['family_name']

        # check if the user exist then login if not then register
        User = get_user_model()
        print('reach try')
        try:
            print('try now to get info')
            user = User.objects.get(provider_id=google_id)
            print(f'user in tyr {user}')
        except User.DoesNotExist:
            print('except')
            user = User.objects.create(
                email=email, provider_id=google_id, provider='Google',
                first_name=first_name, last_name=last_name, access_token=access_token, refresh_token=refresh_token)
            print(f'user in except {user}')
            user.set_unusable_password()
            user.save()

        login(request, user)
        return redirect(env('FRONTEND_URL') + '/')
    except Exception as e:
        print(f'error due to {e}')
        return JsonResponse({'status': False, 'message': f'Error becuase of {e}'})