from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import ensure_csrf_cookie
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({
        "ok": True
    })


def register_v1(request):
    if request.method == 'POST':
        # IN THE MIDDLEWARE THE BODY BECOME new_body
        body = getattr(request, 'new_body')
        User = get_user_model()

         # extracted important Info
        username = body['username']
        email = body['email']
        first_name = body.get('first_name', '')
        last_name = body.get('last_name', '')
        password = body['password']

        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': False, 'message': 'User Already Exists'}, status=400)
        try:
            # create an User object in DB
            with transaction.atomic():
                user = User.objects.create_user(
                                username=username, email=email, is_active=False,
                                first_name=first_name, last_name=last_name, password=password)

                # Generate unique token for the user
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                active_link = f"{env('FRONTEND_URL')}/active-page?uid={uid}&token={token}"


                #send an email
                email = EmailMessage(
                    subject='Activate Your Account',
                    body=f"""
                        Click on the Link Below in order to activate your account and enjoy your Amazing Image in Higher resolution\n
                        {active_link}
                    """,
                    to=[f'{user.email}'])
                email.send(fail_silently=False)
                return JsonResponse({'status': True, "message": "User Must Activate Account"}, status=200)

        except Exception as e:
            return JsonResponse({'status': False, 'message': f'Name or email or password is Empty'}, status=500)
    


def login_v1(request):
    try:
        user = get_user_model()
        body = getattr(request, 'new_body')
        user = authenticate(request, email=body.get('email'), password=body.get('password'))
        if user is None:
            return JsonResponse({'status': False, 'message': 'Invalid Credentials'}, status=401)
        login(request, user)
        return JsonResponse({'status': True, 'data': {'id': user.id, 'first_name': user.first_name}})
    except Exception as e:
        print(f'error because of {e}')
        return JsonResponse({'status': False, 'message': 'Faild to Login'})


def singout(request):
    logout(request)
    return JsonResponse({'status': True, 'Message': "Logout Successfully"}, status=200)


def activateAccount(request):
    if request.method == 'POST':
        body = getattr(request, 'new_body')
        uid = body.get('uid')
        token = body.get('token')
        print(f'token {token}\tuid {uid}')
        User = get_user_model()
        print(f'user model {User}')
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            print(f'user id {user_id}')
            user = User.objects.get(pk=user_id)
            print(f'user object {user}')
        except Exception:
            return JsonResponse({'status': False, 'message': "Can't Activate User Don't Exists"}, status=400)

        if default_token_generator.check_token(user, token):
            print('insid eth check')
            user.is_active = True
            user.save()
            return JsonResponse({'status': True, 'data': {'id': user.id, 'first_name': user.first_name}}, status=201)
        return JsonResponse({'status': False, 'message': "Invalid Token"}, status=400)
