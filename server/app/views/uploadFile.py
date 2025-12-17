from django.http import JsonResponse
from ..form import UploadFileForm


def upload_file(request):
    if request.method == "POST":
        try:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                print("Cleaned data:", form.cleaned_data)
                uploaded_file = form.cleaned_data['file']

                return JsonResponse({'status': True})
            return JsonResponse({'status': False, 'Message': 'Faild to valid the from'})
        except Exception as e:
            print(f'Problem due to {e}')
            return JsonResponse({'status': False, 'Message': "Can't Upload file"})