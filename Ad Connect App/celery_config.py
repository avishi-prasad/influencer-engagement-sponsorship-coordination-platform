from celery import Celery
from celery.beat import PersistentScheduler
from celery.schedules import crontab

celery_app = Celery('tasks', broker='redis://localhost:6379/0')
celery_app.conf.timezone = 'UTC'
celery_app.conf.worker_pool = 'solo'
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.beat_scheduler = PersistentScheduler
celery_app.conf.beat_max_loop_interval = 10  

def setup_celery():
    celery_app.conf.beat_schedule = {
    'monthly_activity_report': {
        'task': 'tasks.schedule_monthly_reports',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),  
    }
    }


    

