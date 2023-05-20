from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import requests
import pymongo
import urllib.parse
from bson.objectid import ObjectId
import base64
import uuid
import boto3, botocore
import random
import datetime
import io

load_dotenv()


# Setting up Flask app
def create_app() -> object:
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'o7'
    app.config["DEBUG"] = True
    app.config['S3_BUCKET'] = os.getenv('S3_BUCKET_NAME')
    app.config['S3_KEY'] = os.getenv('AWS_ACCESS_KEY')
    app.config['S3_SECRET'] = os.getenv('AWS_ACCESS_SECRET')
    app.config['S3_LOCATION'] = f"http://{os.getenv('S3_BUCKET_NAME')}.s3.amazonaws.com/"

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # redirects if user != login
    login_manager.init_app(app)

    return app


# Setting up Mongo Database
def create_db():
    mongo_username = urllib.parse.quote_plus(os.getenv('MONGO_USERNAME'))
    print(mongo_username)
    mongo_password = urllib.parse.quote_plus(os.getenv('MONGO_PASSWORD'))
    print(mongo_password)
    uri = f"mongodb+srv://{mongo_username}:{mongo_password}@neighbourhoodhacks.t7hz7xu.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    db = client.get_database('NeighbourhoodHacks')

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
    return db


db = create_db()
