
from flask import Flask, render_template, request, redirect, url_for
from database import get_connection
from inventory import organize_inventory, search_products, check_low_stock

app = Flask(__name__)


# Get products from MySQL
def get_products():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM products ORDER BY id")
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


# Dashboard
@app.route("/")
def home():
    products = get_products()

    total_products = len(products)
    total_stock = sum(p["quantity"] for p in products)
    low_stock = len(check_low_stock(products))

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_stock=total_stock,
        low_stock=low_stock
    )


# Add Product
@app.route("/add", methods=["GET", "POST"])
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
                """INSERT INTO products
                   (name, aisle, bin, quantity, minimum)
                   VALUES (%s, %s, %s, %s, %s)""",
                (name, aisle, bin_number, quantity, minimum)
            )
            connection.commit()
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for("inventory"))

    return render_template("add_product.html")


# View and search inventory
@app.route("/inventory")
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
        search=keyword
    )


# Update stock quantity
@app.route("/update/<int:product_id>", methods=["POST"])
def update_stock(product_id):

    try:
        change = int(request.form["change"])
    except (ValueError, KeyError):
        return "Enter a valid quantity.", 400

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """UPDATE products
               SET quantity = quantity + %s
               WHERE id = %s AND quantity + %s >= 0""",
            (change, product_id, change)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return "Product not found or insufficient stock.", 400

        connection.commit()
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("inventory"))


if __name__ == "__main__":
    app.run(debug=True)
