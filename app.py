from flask import Flask, render_template

app = Flask(__name__)

@app.route("/apply")
def apply():
    return render_template("apply.html")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/admissions")
def admissions():
    return render_template("admissions.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)