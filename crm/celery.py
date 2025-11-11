import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')


app = Celery('crm')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """A debug task to check Celery worker status."""
    print(f'Request: {self.request!r}')