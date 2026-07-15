from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route("/apply", methods=["GET", "POST"])
def apply():

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        date_of_birth = request.form["date_of_birth"]
        gender = request.form["gender"]
        class_applying = request.form["class_applying"]
        parent_name = request.form["parent_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO applicants
            (first_name, last_name, date_of_birth, gender,
             class_applying, parent_name, phone, email, address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            first_name,
            last_name,
            date_of_birth,
            gender,
            class_applying,
            parent_name,
            phone,
            email,
            address
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("apply.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/admissions")
def admissions():
    return render_template("admissions.html")

@app.route("/admin/applicant/<int:applicant_id>")
def applicant_details(applicant_id):

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM applicants WHERE id = ?",
        (applicant_id,)
    )

    applicant = cursor.fetchone()

    conn.close()

    return render_template(
        "admin/applicant_details.html",
        applicant=applicant
    )

@app.route("/admin/applicants")
def applicants():

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applicants")

    applicants = cursor.fetchall()

    conn.close()

    return render_template(
        "admin/applicants.html",
        applicants=applicants
    )

@app.route("/admin/applicant/<int:applicant_id>/approve")
def approve_applicant(applicant_id):

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE applicants SET status='Approved' WHERE id=?",
        (applicant_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("applicant_details",
                            applicant_id=applicant_id))

@app.route("/admin/applicant/<int:applicant_id>/reject")
def reject_applicant(applicant_id):

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE applicants SET status='Rejected' WHERE id=?",
        (applicant_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("applicant_details",
                            applicant_id=applicant_id))

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)