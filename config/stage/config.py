# Stage environment configuration

class Config:
    """Stage environment configuration"""
    DEBUG = False
    PORT = 8000
    DATABASE_PATH = 'todolist_stage.db'
    HOST = '0.0.0.0'
    SECRET_KEY = 'stage_environment_secret_key'