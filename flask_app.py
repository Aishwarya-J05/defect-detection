from flask import Flask, render_template, request, redirect, url_for, session
import os, base64
from dotenv import load_dotenv
from database.db import login_user, signup_user, save_report, get_user_reports, get_report_stats
from detect import detect_defects
from explain import explain_defect
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

# app = Flask(__name__)
# app.secret_key = "steelsense-secret-key-2024"

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "steelsense-secret-key-2024")

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_HTTPONLY"] = True


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def landing():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        action = request.form.get("action")
        email  = request.form.get("email")
        password = request.form.get("password")

        if action == "login":
            user, err = login_user(email, password)
            if err:
                error = err
            else:
                session["user_id"]    = str(user.id)
                session["user_email"] = user.email
                session["user_name"]  = user.user_metadata.get("full_name", email.split("@")[0]) if user.user_metadata else email.split("@")[0]
                return redirect(url_for("dashboard"))

        elif action == "signup":
            full_name = request.form.get("full_name")
            user, err = signup_user(email, password, full_name)
            if err:
                error = err
            else:
                user, err = login_user(email, password)
                if user:
                    session["user_id"]    = str(user.id)
                    session["user_email"] = user.email
                    session["user_name"]  = full_name
                    return redirect(url_for("dashboard"))

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))

@app.route("/dashboard")
@login_required
def dashboard():
    stats = get_report_stats(session["user_id"])
    return render_template("dashboard.html",
        user_name=session["user_name"],
        stats=stats
    )

@app.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    result = None
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            # Save uploaded file temporarily
            temp_path = f"temp_{file.filename}"
            file.save(temp_path)

            # Read original image as base64
            with open(temp_path, "rb") as f:
                original_b64 = base64.b64encode(f.read()).decode()

            # Run YOLO detection + Gemini explanation (all in one)
            detection_result = detect_defects(temp_path)
            detections = detection_result["detections"]
            annotated_path = detection_result["annotated_image"]

            # Read annotated image as base64
            with open(annotated_path, "rb") as f:
                annotated_b64 = base64.b64encode(f.read()).decode()

            # Cleanup temp files
            os.remove(temp_path)
            if os.path.exists(annotated_path):
                os.remove(annotated_path)

            # Save to Supabase
            save_report(
                user_id=session["user_id"],
                image_name=file.filename,
                annotated_image_b64=annotated_b64,
                detections=detections
            )

            result = {
                "original_image": original_b64,
                "annotated_image": annotated_b64,
                "detections": detections
            }

    return render_template("analyze.html",
        user_name=session["user_name"],
        result=result
    )

@app.route("/reports")
@login_required
def reports():
    user_reports = get_user_reports(session["user_id"])
    return render_template("reports.html",
        user_name=session["user_name"],
        reports=user_reports
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)