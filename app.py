from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

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
        passport = request.files["passport"]
        birth_certificate = request.files["birth_certificate"]

        passport_filename = secure_filename(passport.filename)
        birth_certificate_filename = secure_filename(birth_certificate.filename)

        passport.save(
            os.path.join(
                "static/uploads/passports",
                passport_filename
            )
        )

        birth_certificate.save(
            os.path.join(
                "static/uploads/birth_certificates",
                birth_certificate_filename
            )
        )
        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO applicants
        (first_name, last_name, date_of_birth, gender,
         class_applying, parent_name, phone, email,
         address, passport, birth_certificate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
         first_name,
        last_name,
        date_of_birth,
        gender,
        class_applying,
        parent_name,
        phone,
        email,
        address,
        passport_filename,
        birth_certificate_filename
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

    search = request.args.get("search", "")

    if search:
        cursor.execute("""
            SELECT *
            FROM applicants
            WHERE first_name LIKE ?
            OR last_name LIKE ?
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM applicants")

    applicants = cursor.fetchall()

    conn.close()

    return render_template(
        "admin/applicants.html",
        applicants=applicants,
        search=search
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


@app.route("/admin/dashboard")
def admin_dashboard():

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Total applicants
    cursor.execute("SELECT COUNT(*) FROM applicants")
    total = cursor.fetchone()[0]

    # Pending applicants
    cursor.execute("SELECT COUNT(*) FROM applicants WHERE status='Pending'")
    pending = cursor.fetchone()[0]

    # Approved applicants
    cursor.execute("SELECT COUNT(*) FROM applicants WHERE status='Approved'")
    approved = cursor.fetchone()[0]

    # Rejected applicants
    cursor.execute("SELECT COUNT(*) FROM applicants WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin/dashboard.html",
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected
    )

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)