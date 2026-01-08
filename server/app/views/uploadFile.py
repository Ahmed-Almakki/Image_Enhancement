from django.conf import settings
from django.http import JsonResponse
import os
from ..form import UploadFileForm
from ..models import Document
from ..tasks import EnhanceImage


def upload_file(request):
    if request.method == "POST":
        try:
            form = UploadFileForm(request.POST, request.FILES)
            # Check if form valid
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                fileName = form.cleaned_data['title']

                lr_img = Document.objects.create(
                    user=request.user,
                    title=fileName,
                    image=uploaded_file 
                )
                typeImage = lr_img.title.split('.')[-1]
                imagePath = os.path.join(settings.MEDIA_ROOT, str(lr_img.image))
                print(f'the imagte is {imagePath}')
                EnhanceImage.delay(lr_img.id, imagePath, typeImage)
                return JsonResponse({'status': True})
            return JsonResponse({'status': False, 'Message': 'Faild to valid the from'}, status=400)
        except Exception as e:
            print(f'Problem due to {e}')
            return JsonResponse({'status': False, 'Message': "Can't Upload file"}, status=400)

