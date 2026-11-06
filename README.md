# 📦 Inventory Stock Tracker

A Flask and MySQL-based Inventory Management System designed to simplify warehouse inventory management, stock monitoring, and product tracking.

## 🚀 Features

- **Admin Authentication:** Secure admin login and logout functionality.
- **Dashboard:** Displays total products, total stock, low-stock items, aisles and bins used.
- **Inventory Management:** View and organize products by aisle and bin.
- **Add Products:** Add new products with quantity and minimum stock levels.
- **Search Products:** Quickly find products in the inventory.
- **Update Stock:** Increase or decrease product quantities.
- **Low Stock Detection:** Automatically identifies products that reach or fall below their minimum stock level.
- **Delete Products:** Remove products from the inventory.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| MySQL | Database management |
| HTML5 | Frontend structure |
| CSS3 | Styling and UI |
| JavaScript | Frontend interactions |
| Git & GitHub | Version control |

## 📁 Project Structure

```text
Inventory-Stock-Tracker/
│
├── app.py
├── database.py
├── inventory.py
├── init_admin.py
├── test_db.py
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── inventory.html
│   ├── add_product.html
│   ├── update_stock.html
│   ├── low_stock.html
│   ├── login.html
│   └── sidebar.html
│
├── .gitignore
└── README.md
```

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/SAMS-ENGINEER/Inventory-Stock-Tracker.git
```

### 2. Navigate to the Project Directory

```bash
cd Inventory-Stock-Tracker
```

### 3. Install Dependencies

```bash
pip install flask mysql-connector-python python-dotenv
```

### 4. Configure MySQL Database

Create a MySQL database and configure your database credentials in a `.env` file in the project root.

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=your_database_name

SECRET_KEY=your_secret_key

ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_admin_password
```

Replace the placeholder values with your own credentials.

### 5. Initialize Admin Account

```bash
python init_admin.py
```

This creates the admin table and initializes the admin account.

**Note:** The MySQL `products` table must also be created with the required columns: `id`, `name`, `aisle`, `bin`, `quantity`, and `minimum`.

### 6. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## 🔐 Security

- Admin authentication protects application routes.
- Passwords are stored as secure password hashes.
- Database credentials and secret keys are configured through environment variables.
- The `.env` file should never be committed to GitHub.

## 🎯 Project Objective

The objective of this project is to develop a simple and efficient inventory management solution that helps users maintain stock records, monitor product availability, and manage warehouse inventory through a web-based interface.

## 👨‍💻 Developer

**SAMS-ENGINEER**

GitHub: https://github.com/SAMS-ENGINEER

---

⭐ If you find this project interesting, feel free to explore the repository!
