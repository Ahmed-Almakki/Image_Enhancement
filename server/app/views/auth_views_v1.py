from django.contrib.auth import authenticate, login, get_user_model
from django.http import JsonResponse
from django.middleware.csrf import get_token
import json


def csrf_token(request):
    return JsonResponse({'token': get_token(request)})


def register_v1(request):
    try:
        if request.method == 'POST':
            body = json.loads(request.body.decode('utf-8'))
            username = body['username']
            email = body['email']
            first_name = body.get('first_name', '')
            last_name = body.get('last_name', '')
            password = body['password']
            user = get_user_model().objects.create_user(username=username, email=email,
                                                        first_name=first_name, last_name=last_name, password=password)
            print('created', user)
            return JsonResponse({'status': True, "message": "Successfully Create User"}, status=201)
        return JsonResponse({'status': False, 'message': "Can not create User"}, status=401)
    except Exception as e:
        print(f'error is becuase\n{e}')
        return JsonResponse({'status': False, 'message': f'Can not create user becuase {e}'}, status=400)


def login_v1(request):
    body = json.loads(request.body.decode('utf-8'))
    print(f'user name {body.get("email")}\n{body.get("password")}')
    user = authenticate(request, email=body.get('email'), password=body.get('password'))
    print('user auth', user)
    if user is None:
        return JsonResponse({'status': False, 'message': 'Invalid Credentials'}, status=401)
    login(request, user)
    return JsonResponse({'status': True, 'message': 'Successfully LoggedIN'})
