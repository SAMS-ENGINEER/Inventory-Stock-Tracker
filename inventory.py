
# Organize products by aisle and bin
def organize_inventory(products):
    warehouse = {}

    for product in products:
        aisle = product["aisle"]
        bin_number = product["bin"]

        if aisle not in warehouse:
            warehouse[aisle] = {}

        if bin_number not in warehouse[aisle]:
            warehouse[aisle][bin_number] = []

        warehouse[aisle][bin_number].append(product)

    return warehouse


# Search products by ID or name
def search_products(products, keyword):
    results = []

    for product in products:
        if (keyword.lower() in product["name"].lower()
                or keyword == str(product["id"])):
            results.append(product)

    return results


# Find products with low stock
def check_low_stock(products):
    low_stock_items = []

    for product in products:
        if product["quantity"] <= product["minimum"]:
            low_stock_items.append(product)

    return low_stock_items
