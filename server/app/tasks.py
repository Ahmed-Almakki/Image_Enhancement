from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.files.base import ContentFile
from django.utils import timezone
import io
import numpy as np
import os
from PIL import Image
import tensorflow as tf
from datetime import timedelta

from .models import Document, CeleryTask, TaskStatus


AI_MODELS = {}

@shared_task
def SendEmail(subject, email, message):
        sendemail = EmailMessage(
            subject=subject,
            body=message,
            to=[f'{email}']
        )
        sendemail.send(fail_silently=True)
        return 'Done'


@shared_task(bind=True)
def EnhanceImage(self, id, imagePath, type):
        try:
                if 'esrgan' not in AI_MODELS:
                        print(f"Worker {os.getpid()}: Loading Model for the first time...")
                        modelPath = os.path.join(settings.BASE_DIR, 'server', 'app', 'ai', 'ESRGAN')
                        AI_MODELS['esrgan'] = tf.saved_model.load(modelPath)
                
                model = AI_MODELS['esrgan']
                print(list(model.signatures.keys()))

                CeleryTask.objects.filter(task_id=self.request.id).update(status=TaskStatus.STARTED)
                document = Document.objects.filter(id=id).first()

                image = tf.io.read_file(imagePath)
                if type == 'png':
                        image = tf.image.decode_png(image, channels=3)
                else:
                        image = tf.image.decode_image(image, channels=3)
                
                image = tf.cast(image, tf.float32)
                image_x = tf.expand_dims(image, axis=0)

                result = model(image_x)
                image_y = np.squeeze(result, axis=0)

                # Convert to PNG in memory
                # result_image = (image_y * 255).astype(np.uint8)
                result_image = np.clip(image_y, 0, 255).astype(np.uint8)
                img_pil = Image.fromarray(result_image)
                buffer = io.BytesIO()
                img_pil.save(buffer, format="PNG")
                buffer.seek(0)

                # Delete old image file
                if document.image:
                        document.image.delete(save=False)

                # Save new image
                document.image.save("enhanced.png", ContentFile(buffer.read()), save=True)
                CeleryTask.objects.filter(task_id=self.request.id).update(status=TaskStatus.FINISH)
                return f"Enhanced image saved for document {document.id}"
        except Exception as e:
                return f"Faied to save or process the image due to {e}"


@shared_task
def old_image_delete_task():
        print('inside the old image delete')
        beforHour = timezone.now() - timedelta(hours=2)
        old_celeries = CeleryTask.objects.filter(created_at__lt=beforHour, status=TaskStatus.FINISH)
        tasks = Document.objects.filter(created_at__lt=beforHour)

        for item in tasks:
                if item.image and os.path.exists(str(item.image)):
                        os.remove(str(item.image))
        tasks.delete()
        old_celeries.delete()
        return "done executing the schedule task"