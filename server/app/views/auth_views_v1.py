from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({
        "ok": True
    })


def register_v1(request):
    try:
        if request.method == 'POST':
            # IN THE MIDDLEWARE THE BODY BECOME new_body
            body = getattr(request, 'new_body')
            print(f'regist body {body}')
            username = body['username']
            email = body['email']
            first_name = body.get('first_name', '')
            last_name = body.get('last_name', '')
            is_active = body.get('is_active')
            password = body['password']
            user = get_user_model().objects.create_user(username=username, email=email, is_active=is_active,
                                                        first_name=first_name, last_name=last_name, password=password)
            return JsonResponse({'status': True, "message": "Successfully Create User"}, status=201)
        return JsonResponse({'status': False, 'message': "Can not create User"}, status=401)
    except Exception as e:
        return JsonResponse({'status': False, 'message': f'Can not create user because {e}'}, status=400)


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

