from app import app
from flask import render_template
from flask_cors import CORS, cross_origin

@app.route("/admin/dashboard")
@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def admin_dashboard():
    return render_template("admin/dashboard.html")

@app.route("/admin/profile")
@cross_origin(origins=app.config["CORS_ALLOWED_URLS"])
def admin_profile():
    return "Admin profile"
