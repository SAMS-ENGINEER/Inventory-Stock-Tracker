import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from database import get_connection

load_dotenv()

username = os.getenv("ADMIN_USERNAME")
password = os.getenv("ADMIN_PASSWORD")

if not username or not password:
    raise ValueError("Admin credentials missing in .env")

connection = get_connection()
cursor = connection.cursor()

try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute(
        "SELECT id FROM admins WHERE username = %s",
        (username,)
    )

    if cursor.fetchone():
        print("Admin already exists!")
    else:
        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO admins (username, password_hash)
            VALUES (%s, %s)
        """, (username, password_hash))

        connection.commit()
        print("Admin account created successfully!")

finally:
    cursor.close()
    connection.close()