from app import app

from flask import Flask, render_template, Blueprint, jsonify, request, current_app

import json
import time
import os
import math
import subprocess

#from app import r
#from app import q


import redis
from rq import Queue, Connection




# Globals
projectName = ""
projectName = ""

jobID = ""


# sample data
# {
#        "IWatermaker": {
#            "files": [
#                 {
#                    "fileName": "vid.mov",
#                    "fileType": "mov",
#                    "fileSize": "10004",
#                    "isBaseFile": true,
#                    "width": "1080",
#                    "height": "1920",
#                    "x": "50",
#                    "y": "100",
#                    "r": "90"
#                },
#                {
#                    "fileName": "pic.png",
#                    "fileType": "png",
#                    "fileSize": "10004",
#                    "isBaseFile": false,
#                    "width": "250",
#                    "height": "100",
#                    "x": "100",
#                    "y": "200",
#                    "r": "90"
#                }
#            ]
#        }
#    }

def watermarkBL(req):
    print("validate files")
    global projectPath
    global projectName
    global jobID

    data = req.form

    print(data)
    print(data.getlist("WMData"))
    fileData = json.loads(data.getlist("WMData")[0])
    
    print(fileData["IWatermaker"])

    if req.files:
        uploaded_files = req.files.getlist('files')
        fileMetadata = fileData["IWatermaker"]["files"]

        ## Generate project directory ##
        createProject()

        print()
        print("PROJECT CREATED", uploaded_files)
        print()

        for obj in uploaded_files:
            print("FILE IN UPLOADED FILEs")

            currFileMetadata = ""

            # check file name for text
            if obj.filename == "":
                print("No filename")
                return redirect(request.url)

            # check if file exists in json and
            for f in fileMetadata:
                print(f)
                if f["fileName"] == obj.filename:
                    currFileMetadata = f

            if (currFileMetadata == ""):
                print("file does not exist")
                return redirect(request.url)

            # check file type
            if not allowed_file(obj.filename):
                print("File type not exist")
                return redirect(request.url)

            # TODO - make secure file name
            
            # TODO - output file name variances

            # upload
            print("")
            print("OBJ.FILENAME", os.path.join(projectPath, obj.filename))
            obj.save(os.path.join(projectPath, obj.filename))

        # watermark
        #ffmpeg(projectPath, projectName, fileMetadata)
        with Connection(redis.from_url(current_app.config["REDIS_URL"])):
            q = Queue()
            job = q.enqueue(ffmpeg, projectPath, projectName, fileMetadata, job_timeout=app.config["TIMOUT_TIME"])
        
        print("JOB", job)
        jobID = job.get_id()
        
        print()
        print("JobID", jobID)
        print()

        return {"jobId" : jobID, "projectName" : f"project_{projectName}"}
        #return {"jobId" : "jobID", "projectName" : f"project_{projectName}"}
    return None 




def createProject():
    ts = time.time()
    global projectPath
    global projectName

    projectName = str(ts).replace('.', '-')
    projectPath = app.config["PROJECTS_PATH"] + \
        "project_" + str(ts).replace('.', '-')
    fileNames = []

    os.makedirs(projectPath)
    


def ffmpeg(projectPath, projectName, fileMetadata):
    print("starting FFMPEG")

    baseFileName = ""
    baseFileType = ""
    wmFiles = []
    for fle in fileMetadata:
        if fle["isBaseFile"] == True:
            baseFileName = projectPath + "/" + fle["fileName"]
            baseFileType = projectPath + "/" + fle["fileType"]
        else:
            wmFiles.append({
                "path": projectPath + "/" + fle["fileName"],
                "w": fle["width"],
                "h": fle["height"],
                "x": fle["x"],
                "y": fle["y"],
                "r": fle["r"]})

    fileOutputPathAndName = projectPath + "/output." + "mp4"  # baseFileType

    deepWatermark = app.config["IMAGES_PATH"] + "companyWatermark.png"

    # To scale after the rotate: (just replaced and with desired values.
    # -filter_complex "[1:v] rotate=30*PI/180:c=none:ow=rotw(iw):oh=roth(ih) [rotate];[rotate]scale=<scale_width>:<scale_height>[scale];[0:v][scale] overlay=40:10[out]" -map [out] .......
    # to scale before the rotate: (just replaced and with desired values.
    # -filter_complex "[1:v]scale=<scale_width>:<scale_height>[scale];[scale]rotate=30*PI/180:c=none:ow=rotw(iw):oh=roth(ih) [rotate];[0:v][rotate] overlay=40:10[out]" -map [out] .......

    rotate = str(math.radians(float(wmFiles[0]["r"])))
 
    # scale then rotate WITHOUT DEEP WATERMARK 
    cmdArgs = ["ffmpeg",
               "-i", "\"" + baseFileName + "\" ",
               "-i", "\"" + wmFiles[0]["path"] + "\" ",
               "-filter_complex", "\"[1:v] scale=" + wmFiles[0]["w"] + ":" + wmFiles[0]["h"] + "[scale];" +
               "[scale]rotate=" + rotate + ":c=none:ow=rotw(" + rotate + "):oh=roth(" + rotate + ")" + "[rotate];" +
               "[0:v][rotate] overlay=" + wmFiles[0]["x"] +
               ":" + wmFiles[0]["y"] + "\"",
               "-c:a", "copy",
               fileOutputPathAndName,
               "-preset", "ultrafast", "-y"]


   # scale then rotate WITH DEEP WATERMARK
    cmdArgs = ["/code/ffmpeg",
               "-i", "\"" + baseFileName + "\" ",
               "-i", "\"" + wmFiles[0]["path"] + "\" ",
               "-i", "\"" + deepWatermark + "\" ",

               "-filter_complex", "\"[1:v] scale=" + wmFiles[0]["w"] + ":" + wmFiles[0]["h"] + "[scale];" +
               "[scale]rotate=" + rotate + ":c=none:ow=rotw(" + rotate + "):oh=roth(" + rotate + ")" + "[rotate];" +
               "[0:v][rotate] overlay=" + wmFiles[0]["x"] +
               ":" + wmFiles[0]["y"] + "[v1];" +
               
               "[2:v] scale=282:87[scale];" +
               "[scale]rotate=" + "0" + ":c=none:ow=rotw(" + "0" + "):oh=roth(" + "0" + ")" + "[rotate];" +
               "[v1][rotate] overlay=x=(15):y=(main_h-overlay_h - 15)"+
                "\"",

               "-c:a", "copy",
               fileOutputPathAndName,
               "-preset", "ultrafast", "-y"]

    # rotate then scale
    #cmdArgs = ["ffmpeg",
    #           "-i", baseFileName,
    #           "-i", wmFiles[0]["path"],
    #           "-filter_complex", 
    #           "\"[1:v] rotate=" + rotate + ":c=none:ow=rotw(" + rotate + "):oh=roth(" + rotate + ")" + "[rotate];" +
    #           "[rotate] scale=" + wmFiles[0]["w"] + ":" + wmFiles[0]["h"] + "[scale];" +
    #           "[0:v][scale] overlay=" + wmFiles[0]["x"] +
    #           ":" + wmFiles[0]["y"] + "\"",
    #           "-c:a", "copy",
    #           fileOutputPathAndName,
    #           "-preset", "ultrafast", "-y"]

    cmd = generateCommand(cmdArgs)
    print(cmd)

    subprocess.call(cmd, shell=True)


def generateCommand(cmdArgs):
    cmd = ""
    for i in cmdArgs:
        cmd = cmd + " " + i

    return cmd


def allowed_file(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_FILE_EXTENSIONS"]:
        return True
    else:
        return False
