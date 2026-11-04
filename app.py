
from flask import Flask, render_template, request, redirect, url_for
from database import get_connection
from inventory import organize_inventory, search_products, check_low_stock

app = Flask(__name__)


# ---------------------------------------
# Get all products from MySQL
# ---------------------------------------
def get_products():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM products ORDER BY id")
        return cursor.fetchall()
    finally:
        cursor.close()
        connection.close()


# ---------------------------------------
# Dashboard
# ---------------------------------------
@app.route("/")
def home():
    products = get_products()

    # Total number of products
    total_products = len(products)

    # Total quantity of all products
    total_stock = sum(
        product["quantity"] for product in products
    )

    # Products with low stock
    low_stock_products = check_low_stock(products)
    low_stock = len(low_stock_products)

    # Count unique aisles
    aisles_used = len(set(
        product["aisle"] for product in products
    ))

    # Count unique aisle and bin locations
    bins_used = len(set(
        (product["aisle"], product["bin"])
        for product in products
    ))

    # Show 5 most recently added products
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


# ---------------------------------------
# Add Product
# ---------------------------------------
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


# ---------------------------------------
# View and Search Inventory
# ---------------------------------------
@app.route("/inventory")
def inventory():
    products = get_products()

    keyword = request.args.get("search", "").strip()

    if keyword:
        products = search_products(products, keyword)

    # Organize products by aisle and bin
    warehouse = organize_inventory(products)

    return render_template(
        "inventory.html",
        products=products,
        warehouse=warehouse,
        search=keyword,
        active_page="inventory"
    )


# ---------------------------------------
# Update Stock Page
# ---------------------------------------
@app.route("/update-stock")
def update_stock_page():
    products = get_products()

    return render_template(
        "update_stock.html",
        products=products,
        active_page="update"
    )


# ---------------------------------------
# Update Stock Quantity
# ---------------------------------------
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
            """
            UPDATE products
            SET quantity = quantity + %s
            WHERE id = %s
            AND quantity + %s >= 0
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

    # Return to Update Stock page
    return redirect(url_for("update_stock_page"))


# ---------------------------------------
# Low Stock Page
# ---------------------------------------
@app.route("/low-stock")
def low_stock_page():
    products = get_products()

    # Filter low-stock products
    low_products = check_low_stock(products)

    return render_template(
        "low_stock.html",
        products=low_products,
        active_page="low_stock"
    )


# ---------------------------------------
# Run Flask Application
# ---------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
