import sqlite3

connection = sqlite3.connect("school.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS applicants (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    first_name TEXT NOT NULL,

    last_name TEXT NOT NULL,

    date_of_birth TEXT NOT NULL,

    gender TEXT NOT NULL,

    class_applying TEXT NOT NULL,

    parent_name TEXT NOT NULL,

    phone TEXT NOT NULL,

    email TEXT,

    address TEXT,

    passport TEXT,

    birth_certificate TEXT,

    status TEXT DEFAULT 'Pending',

    date_applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

connection.commit()

connection.close()

print("Database created successfully!")