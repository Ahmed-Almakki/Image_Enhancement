from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
import os
from ..form import UploadFileForm
from ..models import Document, CeleryTask
from ..tasks import EnhanceImage


def upload_file(request):
    if request.method == "POST":
        print('inside teh upload')
        try:
            form = UploadFileForm(request.POST, request.FILES)
            # Check if form valid
            print('before teh chekc', form)
            if form.is_valid():
                uploaded_file = form.cleaned_data['file']
                fileName = form.cleaned_data['title']

                print('insid the check request to create')
                lr_img = Document.objects.create(
                    user=request.user,
                    title=fileName,
                    image=uploaded_file 
                )
                print(f'create teh low res image {lr_img}')
                typeImage = lr_img.title.split('.')[-1]
                imagePath = os.path.join(settings.MEDIA_ROOT, str(lr_img.image))
                
                print('now well invode the task')
                task = EnhanceImage.apply_async(args=[lr_img.id, imagePath, typeImage], countdown=10)
                print(f"invokd task and this is the id {task.id}")
                CeleryTask.objects.create(
                    user=request.user,
                    task_id=task.id
                )
                print('create the celery task')
                return JsonResponse({'status': True, "data": task.id})
            return JsonResponse({'status': False, 'Message': 'Faild to valid the from'}, status=400)
        except Exception as e:
            print(f'Problem due to {e}')
            return JsonResponse({'status': False, 'Message': "Can't Upload file"}, status=400)


def checkTask(request, task_id):
    def stream():
        loop = True
        try:
            while loop:
                try:
                    task = CeleryTask.objects.filter(task_id=task_id).first()
                    yield f"data: {task.status}\n\n"
                except Exception:
                    yield f"data: ERROR: task not found\n\n"
                    loop = False

                if task.status in ["FINISH", "FAILURE"]:
                    if task.status == 'FINISH':
                        img = Document.objects.filter(user=task.user).first()
                        img_path = str(img.image)
                        yield f"data: {img_path}**DONE\n\n"
                    loop = False

                time.sleep(2)
        except Exception:
            yield "data: ERROR: Somthing went wrong"
    return StreamingHttpResponse(stream(), content_type="text/event-stream")
            

