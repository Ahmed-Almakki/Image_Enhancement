from django.conf import settings
from django.http import JsonResponse
import os.path
from ..form import UploadFileForm
from ..ai.enhanceImage import ApplyEhnancment


MEDIA_PATH = os.path.join('server', 'app', 'media')

def upload_file(request):
    if request.method == "POST":
        try:
            form = UploadFileForm(request.POST, request.FILES)
            # Check if form valid
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                fileName = form.cleaned_data['title']

                # Check for path existance if not create one and save it in temp folder
                temp_dir = os.path.join(settings.BASE_DIR, MEDIA_PATH, 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                with open(os.path.join(temp_dir, fileName), 'wb+') as file:
                    for chunck in uploaded_file:
                        file.write(chunck)

                # enhance the image
                ImagePath = os.path.join(temp_dir, fileName)
                EnhancePath = os.path.join(settings.BASE_DIR, 'server', 'app', 'media', 'enhance')
                EnhancedImage = ApplyEhnancment(ImagePath)

                os.makedirs(EnhancePath, exist_ok=True)
                EnhancedImage.save(f'{EnhancePath}/{fileName}')

                return JsonResponse({'status': True})
            return JsonResponse({'status': False, 'Message': 'Faild to valid the from'})
        except Exception as e:
            print(f'Problem due to {e}')
            return JsonResponse({'status': False, 'Message': "Can't Upload file"})

