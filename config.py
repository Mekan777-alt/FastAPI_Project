import json
import os
import pyrebase
from dotenv import load_dotenv
from firebase_admin import credentials
from pydantic import BaseConfig

load_dotenv()


class Config(BaseConfig):

    DB_NAME = os.getenv("DBNAME")
    DB_USER = os.getenv("DBUSER")
    DB_PASSWORD = os.getenv("DBPASSWORD")
    DB_HOST = os.getenv("DBHOST")
    DB_PORT = os.getenv("DBPORT")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")


settings = Config()


cred = credentials.Certificate("app-house-d0ac1-firebase-adminsdk-g0nda-1e43074d18.json")
pb = pyrebase.initialize_app(json.load(open("test_config.json")))
