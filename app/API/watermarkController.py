from app import app

from werkzeug.utils import secure_filename
from flask import Flask, render_template, Blueprint, jsonify, request, current_app, send_from_directory
import os, shutil
import subprocess
import time
import json
import math
from treeHandler import treeHandler
from flask_cors import CORS, cross_origin

from app.BusinessLayer import watermarkBL


import redis
from rq import Queue, Connection

@app.route("/watermarker", methods=["GET", "POST"])
def watermarkAPI():
    print("WATERMARK API")

    if request.method == "POST":
        result = watermarkBL.watermarkBL(request)

    return result


@app.route("/watermarker/tasks/<task_id>", methods=["GET"])
def get_project_status(task_id):
    started_at = None
    ended_at = None
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()

        job = q.fetch_job(task_id)
        if (job != None):
            started_at = job.started_at
            ended_at = job.ended_at
        
    return {"jobStartedAt" : started_at, "jobEndedAt": ended_at}

@app.route("/testGetReq", methods=["GET"])
@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def getTest():
    return {"test": "test email", "code": "test code"}

@app.route("/watermarker/deleteAllProject")
def deleteAllProject():
    min_15 = 15 * 60
    timeMinus15 = time.time() - min_15
    projectOlderThan15 = "project_" + str(timeMinus15).replace('.', '-')

    folder = app.config["PROJECTS_PATH"] 
    for currProject in os.listdir(folder):
        if (projectOlderThan15 > currProject):
            file_path = os.path.join(folder, currProject)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    print("DELETING OBJECTS")
    return "All projects deleted."



@app.route("/download/<projectPath>/<file>")
def download(projectPath, file):
    print("projectPath", projectPath)
    print("vid", file)

    x = app.config["PROJECTS_PATH"] + projectPath + "/" 
    
    try:
        return send_from_directory(x, filename=file, as_attachment=True)
    except FileNotFoundError:
        return x


@app.route("/checkPath")
def checkPath():
    th=treeHandler()
    fileTuple=th.getFiles('app')
    print(fileTuple)
    x = os.getcwd() + "/app/app/static/projects/"
    return str(fileTuple)