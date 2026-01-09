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
                MODEL_PATH = os.path.join(
                        settings.BASE_DIR, 'server', 'app', 'ai', 'btsrn_vgg_epoch_50.h5'
                )
                CeleryTask.objects.filter(task_id=self.request.id).update(status=TaskStatus.STARTED)
                document = Document.objects.filter(id=id).first()
                model = tf.keras.models.load_model(MODEL_PATH, compile=False)
                image = tf.io.read_file(imagePath)
                if type == 'png':
                        image = tf.image.decode_png(image, channels=3)
                else:
                        image = tf.image.decode_image(image, channels=3)
                image = tf.cast(image, tf.float32) / 255.0

                image_x = tf.expand_dims(image, axis=0)
                result = model.predict(image_x)

                image_y = np.squeeze(result, axis=0)

                # Convert to PNG in memory
                result_image = (image_y * 255).astype(np.uint8)
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
        old_celeries = CeleryTask.objects.filter(created_at__lt=beforHour)
        tasks = Document.objects.filter(created_at__lt=beforHour)

        for item in tasks:
                if item.image and os.path.exists(str(item.image)):
                        os.remove(str(item.image))
        tasks.delete()
        return "done executing the schedule task"