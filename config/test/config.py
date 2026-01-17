# Test environment configuration

class Config:
    """Test environment configuration"""
    DEBUG = True
    PORT = 5000
    DATABASE_PATH = 'todolist_test.db'
    HOST = '127.0.0.1'
    SECRET_KEY = 'test_environment_secret_key'