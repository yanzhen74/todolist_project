# Live environment configuration

class Config:
    """Live environment configuration"""
    DEBUG = False
    PORT = 8000
    DATABASE_PATH = '/var/lib/todolist/todolist_live.db'
    HOST = '0.0.0.0'
    SECRET_KEY = 'live_environment_secret_key'