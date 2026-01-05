from .celery import app as celery_app

"""
To ensure the Celery app is loaded when Django starts (so that @shared_task works),
you must modify the __init__.py in your project folder.
"""
__all__ = ('celery_app')