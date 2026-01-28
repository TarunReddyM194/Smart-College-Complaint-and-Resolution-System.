from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "adminsecret"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Education@1",
    database="college_complaint_system"
)

cursor = db.cursor()

@app.route("/")
def home():
    return "Smart College Complaint System Running"

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    student_name = request.form["student_name"]
    student_email = request.form["student_email"]
    complaint_type = request.form["complaint_type"]
    complaint_description = request.form["complaint_description"]

    query = """
    INSERT INTO complaints
    (student_name, student_email, complaint_type, complaint_description)
    VALUES (%s, %s, %s, %s)
    """
    
    values = (
        student_name,
        student_email,
        complaint_type,
        complaint_description
    )

    cursor.execute(query, values)
    db.commit()

    return "Complaint submitted successfully"

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/login")

    status = request.args.get("status")
    search = request.args.get("search")

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if status and status != "all":
        query += " AND status = %s"
        params.append(status)

    if search:
        query += " AND student_name LIKE %s"
        params.append(f"%{search}%")

    cursor.execute(query, tuple(params))
    complaints = cursor.fetchall()

    return render_template("dashboard.html", complaints=complaints)


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/admin_login", methods=["POST"])
def admin_login():
    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":
        session["admin_logged_in"] = True
        return redirect("/admin")
    else:
        return "Invalid username or password"
    
@app.route("/resolve/<int:complaint_id>", methods=["POST"])
def resolve_complaint(complaint_id):
    if not session.get("admin_logged_in"):
        return redirect("/login")

    cursor.execute(
        "UPDATE complaints SET status='Resolved' WHERE complaint_id=%s",
        (complaint_id,)
    )
    db.commit()

    return redirect("/admin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/student")
def student_login_page():
    return render_template("student_login.html")

@app.route("/student_login", methods=["POST"])
def student_login():
    email = request.form["email"]
    password = request.form["password"]

    cursor.execute(
        "SELECT * FROM students WHERE student_email=%s AND student_password=%s",
        (email, password)
    )
    student = cursor.fetchone()

    if student:
        session["student_logged_in"] = True
        session["student_email"] = email
        return redirect("/student_dashboard")
    else:
        return "Invalid student credentials"
    
@app.route("/student_dashboard")
def student_dashboard():
    if not session.get("student_logged_in"):
        return redirect("/student")

    student_email = session.get("student_email")

    cursor.execute(
        "SELECT * FROM complaints WHERE student_email = %s",
        (student_email,)
    )
    complaints = cursor.fetchall()

    return render_template("student_dashboard.html", complaints=complaints)

if __name__ == "__main__":
    app.run(debug=True)
