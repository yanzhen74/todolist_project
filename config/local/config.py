# Local environment configuration

class Config:
    """Local environment configuration"""
    DEBUG = True
    PORT = 5000
    DATABASE_PATH = 'todolist_local.db'
    HOST = '127.0.0.1'
    SECRET_KEY = 'local_development_secret_key'