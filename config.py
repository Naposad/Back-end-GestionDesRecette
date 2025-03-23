import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SECRET_KEY = os.getenv('SECRET_KEY')
    #MAIL_SERVER = 'smtp.googlemail.com'
    #MAIL_PORT = 587
    #MAIL_USE_TLS = True
