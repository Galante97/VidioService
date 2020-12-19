
class Config(object):
    DEBUG = False
    TESTING = False

    ALLOWED_FILE_EXTENSIONS = ["PNG", "JPG",
                               "JPEG", "GIF", "MOV", "MP4", "M4V"]

    SESSION_COOKIE_SECURE = True

    # project paths for deployment
    PROJECTS_PATH = "/app/app/static/projects/"
    IMAGES_PATH = "/app/app/static/img/"
     
    MAX_CONTENT_LENGTH = 200000000  # 200mb
    # MAX_CONTENT_LENGTH = 200000000000 # 200000mb

    TIMOUT_TIME = 300  # 300 seconds / 5 min

    REDIS_URL = "redis://redis:6379/0"
    QUEUES = ["default"]


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
