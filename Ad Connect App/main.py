from flask import Flask
from flask_mail import Mail
from models import db
from config import DevelopmentConfig
from celery_config import setup_celery
import redis
import json

mail=Mail()

def create_app():
    app = Flask(__name__)
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_HOST'] = 'localhost'
    app.config['CACHE_REDIS_PORT'] = 6379
    app.config['CACHE_REDIS_DB'] = 0
    app.config.from_object(DevelopmentConfig)
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
    app.config['MAIL_PORT'] = 587                
    app.config['MAIL_USE_TLS'] = True            
    app.config['MAIL_USE_SSL'] = False           
    app.config['MAIL_USERNAME'] = 'avishiprsd04@gmail.com'  
    app.config['MAIL_PASSWORD'] = 'hidden'
    app.config['MAIL_DEFAULT_SENDER'] = 'avishiprsd04@gmail.com'
    app.config['MAIL_DEBUG'] = True

    mail.init_app(app)
    db.init_app(app)
    
    with app.app_context():
        setup_celery()
        import views
        db.create_all()
    
    return app

def get_cached_data(key):
    cache = redis.Redis(
        host='localhost', 
        port=6379, 
        db=0
    )
    cached_data = cache.get(key)
    if cached_data:
        return json.loads(cached_data)  
    return None

def set_cache(key, value, timeout=10):
    cache = redis.Redis(
        host='localhost', 
        port=6379, 
        db=0
    )
    cache.setex(key, timeout, json.dumps(value))  


app=create_app()

if __name__=="__main__":
    app.run(debug=True)

