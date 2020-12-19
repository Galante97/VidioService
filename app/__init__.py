
from flask import Flask, render_template, request, redirect
import redis
from rq import Queue 
from flask_cors import CORS

app = Flask(__name__)

def create_app(script_info=None):

    #CORS(app) #currently allows all domains, not good

    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
    if app.config["ENV"] == "testing":
        app.config.from_object("config.TestingConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")


    #IMPORT APIS

    from app.API import watermarkController

    from app.API import views
    #from app.API import admin_views


    # shell context for flask cli
    app.shell_context_processor({"app": app})

    return app
