from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
