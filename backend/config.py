import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'hospital.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'hms_jwt_secret_2026'
    broker_url = 'redis://127.0.0.1:6380/0'
    result_backend = 'redis://127.0.0.1:6380/0'
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6380
    CACHE_REDIS_DB = 1
    CACHE_DEFAULT_TIMEOUT = 300
