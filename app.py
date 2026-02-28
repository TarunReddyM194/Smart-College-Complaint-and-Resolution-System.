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

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- STUDENT OPTION ----------------
@app.route("/student_option")
def student_option():
    return render_template("student_option.html")


# ---------------- STUDENT REGISTRATION PAGE ----------------
@app.route("/student_register_page")
def student_register_page():
    return render_template("student_register.html")


# ---------------- STUDENT REGISTER ----------------
@app.route("/student_register", methods=["POST"])
def student_register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    try:
        cursor.execute(
            "INSERT INTO students (student_name, student_email, student_password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()
        return redirect("/student")
    except:
        return "Email already registered. Please login."


# ---------------- STUDENT LOGIN PAGE ----------------
@app.route("/student")
def student_login_page():
    return render_template("student_login.html")


# ---------------- STUDENT LOGIN ----------------
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


# ---------------- STUDENT DASHBOARD ----------------
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

# ---------------- RAISE COMPLAINT PAGE ----------------
@app.route("/raise_complaint")
def raise_complaint():
    if not session.get("student_logged_in"):
        return redirect("/student")

    student_email = session.get("student_email")

    cursor.execute(
        "SELECT student_name FROM students WHERE student_email=%s",
        (student_email,)
    )
    student = cursor.fetchone()

    return render_template(
        "register.html",
        student_name=student[0],
        student_email=student_email
    )

# ---------------- COMPLAINT SUBMISSION ----------------
@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    student_name = request.form["student_name"]
    student_email = request.form["student_email"]
    complaint_type = request.form["complaint_type"]
    complaint_description = request.form["complaint_description"]

    cursor.execute(
        """
        INSERT INTO complaints
        (student_name, student_email, complaint_type, complaint_description)
        VALUES (%s, %s, %s, %s)
        """,
        (student_name, student_email, complaint_type, complaint_description)
    )

    db.commit()
    return redirect("/student_dashboard")


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin_login")
def admin_login_page():
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


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin_login")

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

    # COUNT SUMMARY
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
    resolved_count = cursor.fetchone()[0]

    return render_template(
        "dashboard.html",
        complaints=complaints,
        total_count=total_count,
        pending_count=pending_count,
        resolved_count=resolved_count
    )

# ---------------- RESOLVE COMPLAINT ----------------
@app.route("/resolve/<int:complaint_id>", methods=["POST"])
def resolve_complaint(complaint_id):
    if not session.get("admin_logged_in"):
        return redirect("/admin_login")

    cursor.execute(
        "UPDATE complaints SET status='Resolved' WHERE complaint_id=%s",
        (complaint_id,)
    )
    db.commit()

    return redirect("/admin")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



if __name__ == "__main__":
    app.run(debug=True)
