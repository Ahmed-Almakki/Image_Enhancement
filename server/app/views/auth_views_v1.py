from django.http import JsonResponse


def email_login(request):
    print(f"{request.method}")
    return JsonResponse({'ahmed': 'request'})