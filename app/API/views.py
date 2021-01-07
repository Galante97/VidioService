
from app import app

import redis
from rq import Queue, Connection
from flask import Flask, render_template, Blueprint, jsonify, request, current_app
from flask_cors import CORS, cross_origin


@app.route("/")
@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def index():
    print(app.config)
    return render_template("public/index.html")


@app.route("/about")
@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def about():
    return "This is the about page"


# REDIS TESTS
@app.route("/tasks", methods=["POST"])
@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def run_task():
    task_type = request.form["type"]
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()
        task = q.enqueue(create_task, task_type)
    response_object = {
        "status": "success",
        "data": {
            "task_id": task.get_id()
        }
    }
    return jsonify(response_object), 202

# REDIS TESTS
@app.route("/tasks/<task_id>", methods=["GET"])
@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def get_status(task_id):
    with Connection(redis.from_url(current_app.config["REDIS_URL"])):
        q = Queue()
        task = q.fetch_job(task_id)
    if task:
        response_object = {
            "status": "success",
            "data": {
                "task_id": task.get_id(),
                "task_status": task.get_status(),
                "task_result": task.result,
            },
        }
    else:
        response_object = {"status": "error"}
    return jsonify(response_object)


import time

@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True