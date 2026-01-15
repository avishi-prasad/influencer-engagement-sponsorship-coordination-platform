class Config(object):
    DEBUG=False
    TESTING=False

class DevelopmentConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///project_db.sqlite3'