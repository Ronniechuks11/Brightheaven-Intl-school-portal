from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)
import sqlite3
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "brightheaven_secret_key"

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

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        student_id = request.form["student_id"]
        password = request.form["password"]

        conn = sqlite3.connect("school.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM students WHERE student_id=? AND password=?",
            (student_id, password)
        )

        student = cursor.fetchone()

        conn.close()

        if student:
            session["student"] = student["id"]

            return redirect(url_for("student_dashboard"))

        return "Invalid Student ID or Password"

    return render_template("student_login.html")

@app.route("/student/dashboard")
def student_dashboard():

    if "student" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (session["student"],)
    )

    student = cursor.fetchone()

    conn.close()

    if not student:
        session.pop("student", None)
        return redirect(url_for("login"))

    return render_template(
        "student_dashboard.html",
        student=student
    )

@app.route("/student/logout")
def student_logout():

    session.pop("student", None)

    return redirect(url_for("login"))

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

    if "admin" not in session:
        return redirect(url_for("admin_login"))
    

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

    if "admin" not in session:
        return redirect(url_for("admin_login"))

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
@app.route("/admin/applicant/<int:applicant_id>/approve")
def approve_applicant(applicant_id):

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get applicant
    cursor.execute(
        "SELECT * FROM applicants WHERE id=?",
        (applicant_id,)
    )

    applicant = cursor.fetchone()

    if not applicant:
        conn.close()
        return "Applicant not found", 404

    # Prevent creating another account
    cursor.execute(
        "SELECT id FROM students WHERE applicant_id=?",
        (applicant_id,)
    )

    existing_student = cursor.fetchone()

    if existing_student:
        conn.close()
        return redirect(url_for(
            "applicant_details",
            applicant_id=applicant_id
        ))

    # Generate Student ID
    student_id = f"BHS{2026}{applicant_id:04d}"

    # Temporary password
    temporary_password = f"Bright{applicant_id}!"

    password_hash = generate_password_hash(
        temporary_password
    )

    # Create student account
    cursor.execute("""
        INSERT INTO students
        (
            student_id,
            applicant_id,
            first_name,
            last_name,
            email,
            class_name,
            password_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        applicant["id"],
        applicant["first_name"],
        applicant["last_name"],
        applicant["email"],
        applicant["class_applying"],
        password_hash
    ))

    # Update application status
    cursor.execute(
        """
        UPDATE applicants
        SET status='Approved'
        WHERE id=?
        """,
        (applicant_id,)
    )

    conn.commit()
    conn.close()

    return f"""
    <h2>Application Approved Successfully</h2>

    <p><strong>Student:</strong>
    {applicant["first_name"]} {applicant["last_name"]}</p>

    <p><strong>Student ID:</strong> {student_id}</p>

    <p><strong>Temporary Password:</strong>
    {temporary_password}</p>

    <br>

    <a href="/admin/applicant/{applicant_id}">
        Back to Applicant
    </a>
    """


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
    
    if "admin" not in session:
        return redirect(url_for("admin_login"))

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

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("school.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, password)
        )

        admin = cursor.fetchone()
        conn.close()

        if admin:
            session["admin"] = admin["id"]
            return redirect(url_for("admin_dashboard"))

        return "Invalid username or password"

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin_login"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)