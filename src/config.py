import os


class Config:
    DB_NAME = "business"
    DB_USER = "postgres"
    DB_HOST = "localhost"
    DB_PASSWORD = "thepassword"
    DB_ADMIN_USER = "postgres"
    DB_ADMIN_PASSWORD = "thepassword"
    DB_PORT = 5432
    ENV = "dev"

    #SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_DATABASE_URI =  f'postgresql://{DB_USER}:{DB_PASSWORD}@host.docker.internal:5432/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = '648ab73217495df79ebc3270ebae5893'
    JWT_ACCESS_TOKEN_EXPIRES = 84600


class TestConfig(Config):
    DB_HOST = "business-db"
    '''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'test-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600

    TESTING = True
    DEBUG = True
    ENV = "testing"
    '''

def load_config(testing: bool):
    # Ignore env vars if testing is passed
    if testing:
        return TestConfig

    env = os.getenv("ENV")

    if env == "dev":
        return Config
    elif env == "preprod":
        return TestConfig
    elif env == "prod":
        return Config
    raise RuntimeError("Unexpected value of environment variable `ENV`: ", env)
