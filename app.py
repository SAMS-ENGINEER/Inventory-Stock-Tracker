import os
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

from dotenv import load_dotenv
from werkzeug.security import check_password_hash

from database import get_connection
from inventory import organize_inventory, search_products, check_low_stock


# -------------------- FLASK CONFIGURATION --------------------

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY missing in .env file")


# -------------------- LOGIN PROTECTION --------------------

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# -------------------- DATABASE FUNCTIONS --------------------

def get_products():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM products ORDER BY id")
        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


# -------------------- LOGIN ROUTE --------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if "admin_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM admins WHERE username = %s",
                (username,)
            )

            admin = cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

        if admin and check_password_hash(
            admin["password_hash"], password
        ):

            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]

            return redirect(url_for("home"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# -------------------- LOGOUT ROUTE --------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    session.clear()

    return redirect(url_for("login"))


# -------------------- DASHBOARD --------------------

@app.route("/")
@login_required
def home():

    products = get_products()

    total_products = len(products)

    total_stock = sum(
        product["quantity"] for product in products
    )

    low_stock_products = check_low_stock(products)

    low_stock = len(low_stock_products)

    aisles_used = len(
        set(product["aisle"] for product in products)
    )

    bins_used = len(
        set(
            (product["aisle"], product["bin"])
            for product in products
        )
    )

    recent_products = sorted(
        products,
        key=lambda product: product["id"],
        reverse=True
    )[:5]

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_stock=total_stock,
        low_stock=low_stock,
        low_stock_products=low_stock_products,
        aisles_used=aisles_used,
        bins_used=bins_used,
        recent_products=recent_products,
        active_page="dashboard"
    )


# -------------------- ADD PRODUCT --------------------

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_product():

    if request.method == "POST":

        name = request.form["name"].strip()
        aisle = request.form["aisle"].strip()
        bin_number = request.form["bin"].strip()

        try:
            quantity = int(request.form["quantity"])
            minimum = int(request.form["minimum"])

        except ValueError:
            return "Quantity and minimum must be numbers.", 400

        if not name or not aisle or not bin_number:
            return "All fields are required.", 400

        if quantity < 0 or minimum < 0:
            return "Stock values cannot be negative.", 400

        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO products
                (name, aisle, bin, quantity, minimum)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (name, aisle, bin_number, quantity, minimum)
            )

            connection.commit()

        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("inventory"))

    return render_template(
        "add_product.html",
        active_page="add"
    )


# -------------------- INVENTORY --------------------

@app.route("/inventory")
@login_required
def inventory():

    products = get_products()

    keyword = request.args.get("search", "").strip()

    if keyword:
        products = search_products(products, keyword)

    warehouse = organize_inventory(products)

    return render_template(
        "inventory.html",
        products=products,
        warehouse=warehouse,
        search=keyword,
        active_page="inventory"
    )


# -------------------- UPDATE STOCK PAGE --------------------

@app.route("/update-stock")
@login_required
def update_stock_page():

    products = get_products()

    return render_template(
        "update_stock.html",
        products=products,
        active_page="update"
    )


# -------------------- UPDATE STOCK --------------------

@app.route("/update/<int:product_id>", methods=["POST"])
@login_required
def update_stock(product_id):

    try:
        change = int(request.form["change"])

    except (ValueError, KeyError):
        return "Enter a valid quantity.", 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE products
            SET quantity = quantity + %s
            WHERE id = %s AND quantity + %s >= 0
            """,
            (change, product_id, change)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return "Product not found or insufficient stock.", 400

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("update_stock_page"))


# -------------------- DELETE PRODUCT --------------------

@app.route("/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM products WHERE id = %s",
            (product_id,)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return "Product not found.", 404

        connection.commit()

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("inventory"))


# -------------------- LOW STOCK --------------------

@app.route("/low-stock")
@login_required
def low_stock_page():

    products = get_products()

    low_products = check_low_stock(products)

    return render_template(
        "low_stock.html",
        products=low_products,
        active_page="low_stock"
    )


# -------------------- RUN APPLICATION --------------------

if __name__ == "__main__":
    app.run(debug=True)