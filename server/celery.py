import os
from celery import Celery
from celery.schedules import crontab


# tell the celery the information needed to know found in django setting because celery is completly deffrent program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

app = Celery('server')

# tell celery that your configuration is found in settings.py and it start with CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# celery search for any file that called task.py it know the tasks it need to run is there
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "cleanup-task-every-24-hour": {
        "task": "server.app.tasks.old_image_delete_task",
        "schedule": crontab(minute='*', hour='*')
    }
}