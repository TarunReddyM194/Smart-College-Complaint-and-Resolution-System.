from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Smart College Complaint System is Running"

if __name__ == "__main__":
    app.run(debug=True)
