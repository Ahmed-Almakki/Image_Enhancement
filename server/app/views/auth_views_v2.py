from django.http import JsonResponse
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction
from django.shortcuts import redirect
from google.auth.transport import requests as google_requests
import environ
from google.oauth2 import id_token
import json
from pathlib import Path
import requests
import random
import secrets
from datetime import timedelta
from django.utils import timezone

from ..models import RestPassword
from ..tasks import SendEmail

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


def sendState(request):
    """
    send the url of the Oauth from the backend to front without reveling any info in the front
    """
    from urllib.parse import urlencode
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
        try:
            user = User.objects.get(provider_id=google_id)
        except User.DoesNotExist:
            user = User.objects.create(
                email=email, provider_id=google_id, provider='Google',
                first_name=first_name, last_name=last_name, access_token=access_token, refresh_token=refresh_token)
            user.set_unusable_password()
            user.save()

        # login to create the session id and other things
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect(env('FRONTEND_URL') + '/oauth')  # to be able to go to home page
    except Exception as e:
        return JsonResponse({'status': False, 'message': f'Error because of {e}'})

@login_required
def current_user(request):
    return JsonResponse({
        'data' : {
            'id': request.user.id,
            'first_name': request.user.first_name
        }
    })


def resetPassword(request):
    if request.method == 'POST':
        try:
            body = getattr(request, 'new_body', {})
            
            email = body.get('email')
            if not email:
                return JsonResponse({'status': False, 'message': 'You must Enter Email Addres'}, status= 400)
            
            User = get_user_model()
            user = User.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'status': True, 'message': "If an account exists with this email, you will receive a verification code shortly."})
            
            RestPassword.objects.filter(user=user).delete()

            try:
                with transaction.atomic():
                    otp = f"{random.randint(1000, 9999)}"
                    hashdOtp = make_password(otp)

                    createopt = RestPassword.objects.create(
                        otp=hashdOtp, user=user,
                        expires_at=timezone.now() + timedelta(minutes=5)
                    )
                    emailMessage = f'Your verification code is: {otp}'
                    emailSubject = 'Your Password Rest Code'
                    SendEmail.delay(emailSubject, user.email, emailMessage)
            
                return JsonResponse({'status': True, 'message': "If an account exists with this email, you will receive a verification code shortly."})
            except Exception:
                return JsonResponse({'status': True, 'message': "If an account exists with this email, you will receive a verification code shortly."})
        except Exception:
            return JsonResponse({'status': False, 'message': "If an account exists with this email, you will receive a verification code shortly."})
    return JsonResponse({'status': False, 'message': "Wrong request Method"})


def resendPassword(request):
    if request.method == 'POST':
        messageResponse = {
            'status': True,
            'message':"If an account exists with this email, you will receive a verification code shortly."
            }

        body = getattr(request, 'new_body', {})
        email = body.get('email')
        if not email:
            return JsonResponse(messageResponse)
        
        User = get_user_model()
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse(messageResponse)
        
        RestPassword.objects.filter(user=user).delete()
        try:
            with transaction.atomic():
                otp = f"{random.randint(1000, 9999)}"
                hashdOtp = make_password(otp)

                RestPassword.objects.create(
                    otp=hashdOtp,
                    expires_at=timezone.now() + timedelta(minutes=5),
                    user=user
                )
                
                emailMessage = f'Your verification code is: {otp}'
                emailSubject = 'Your Password Rest Code'
                SendEmail.delay(emailSubject, user.email, emailMessage)
            return JsonResponse(messageResponse)
        except Exception:
            return JsonResponse(messageResponse)
    return JsonResponse({'status': False, 'message': 'Invalid Method'}, status=405)



def checkOtp(request):
    if request.method == 'POST':
        body = getattr(request, 'new_body', {})
        otp = body.get('otp')
        email = body.get('email')
        if not otp or not email:
            return JsonResponse({'status': False, 'message': 'You Must Enter the code'}, status=400)
        try:
            User = get_user_model()
            user = User.objects.filter(email=email).first()
            hashed = RestPassword.objects.filter(user=user).first()
            if not hashed:
                return JsonResponse({'status': False, 'message': 'Invalid or Expired OTP'}, status=400)

            if timezone.now() > hashed.expires_at:
                hashed.delete()
                return JsonResponse({'status': False, 'message': 'OTP expired'}, status=400)

            if hashed.attempt == 5:
                hashed.delete()
                return JsonResponse({'status': False, 'message': 'Too many attempt'}, status=400)

            if not check_password(otp, hashed.otp):
                hashed.attempt += 1
                hashed.save()
                return JsonResponse({'status': False, 'message': 'Invalid OTP'}, status=400)

            hashed.delete()
            return JsonResponse({'status': True, 'message': 'Confirm Password Reset'})
        except Exception:
            return JsonResponse({'status': False, 'message': 'Invalid or Expired OTP'}, status=400)
    return JsonResponse({'status': False, 'message': 'Invalid Method'}, status=405)