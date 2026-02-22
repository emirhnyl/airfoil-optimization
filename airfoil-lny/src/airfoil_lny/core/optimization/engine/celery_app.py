from celery import Celery

celery_app = Celery(
    "airfoil_lny",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
)

celery_app.autodiscover_tasks(["airfoil_lny"])