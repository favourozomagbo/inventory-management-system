import sqlite3
import random

DATABASE_NAME = "inventory.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def generate_barcode():

    digits = 12

    barcode = random.randint(
        10 ** (digits - 1),
        (10 ** digits) - 1
    )
    return str(barcode)


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
             id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            description TEXT,
            category TEXT,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT DEFAULT 'Pieces',
            reorder_level INTEGER DEFAULT 5,
            barcode TEXT UNIQUE,
            supplier_id INTEGER,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
    ''')

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN brand TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN unit TEXT DEFAULT 'Pieces'")
    except sqlite3.OperationalError:
            pass

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN reorder_level INTEGER DEFAULT 5")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN created_at TIMESTAMP")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN updated_at TIMESTAMP")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN unit_price REAL")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN user_id INTEGER")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE sale_items ADD COLUMN unit TEXT")
    except sqlite3.OperationalError:
        pass


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_name TEXT NOT NULL,
        phone TEXT,
        email TEXT
    )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT UNIQUE,
            address TEXT
    )
    """)


    cursor.execute("""
        SELECT id
        FROM customers
        WHERE full_name = ?
    """, ("Walk-in Customer",))

    walk_in_customer = cursor.fetchone()

    if walk_in_customer is None:

        cursor.execute("""
            INSERT INTO customers (
                full_name,
                phone,
                email,
                address
            )
            VALUES (?, ?, ?, ?)
        """, (
            "Walk-in Customer",
            "",
            None,
            ""
        ))


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (customer_id)
          REFERENCES customers(id),
        FOREIGN KEY (product_id) 
        REFERENCES products(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        sale_id INTEGER NOT NULL,

        product_id INTEGER NOT NULL,

        unit TEXT NOT NULL,

        quantity INTEGER NOT NULL,

        unit_price REAL NOT NULL,

        total_price REAL NOT NULL,

        FOREIGN KEY (sale_id) REFERENCES sales(id),

        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        product_id INTEGER NOT NULL,

        supplier_id INTEGER NOT NULL,

        quantity INTEGER NOT NULL,

        purchase_price REAL NOT NULL,

        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(product_id) REFERENCES products(id),

        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)

    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_suppliers (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        product_id INTEGER NOT NULL,

        supplier_id INTEGER NOT NULL,

        FOREIGN KEY (product_id) REFERENCES products(id),

        FOREIGN KEY (supplier_id) REFERENCES suppliers(id),

        UNIQUE(product_id, supplier_id)
    )
""")


    cursor.execute("""
    INSERT OR IGNORE INTO product_suppliers (product_id, supplier_id)
    SELECT product_id, supplier_id
    FROM purchases
""")


    # =====================================
# Migrate old sales into sale_items
# =====================================

    cursor.execute("""
    INSERT INTO sale_items (
        sale_id,
        product_id,
        quantity,
        unit,
        unit_price,
        total_price
    )

    SELECT
        sales.id,
        sales.product_id,
        sales.quantity,
        products.unit,
        COALESCE(
            sales.unit_price,
            products.price
        ),
        sales.total_price

    FROM sales

    JOIN products
    ON sales.product_id = products.id

    WHERE NOT EXISTS (
        SELECT 1
        FROM sale_items
        WHERE sale_items.sale_id = sales.id
    )
""")

    conn.commit()
    conn.close()


def add_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users(username, email, password)
        VALUES (?, ?, ?)
    """, (username, email, password))

    conn.commit()
    conn.close()   


def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    conn.close()

    return user 


def add_product(
    product_name,
    brand,
    description,
    category,
    price,
    quantity,
    unit,
    reorder_level,
    supplier_id
):
    conn = get_db_connection()
    cursor = conn.cursor()

    barcode = generate_barcode()

    cursor.execute("""
        INSERT INTO products (
            name,
            brand,
            description,
            category,
            price,
            quantity,
            unit,
            reorder_level,
            barcode,
            supplier_id,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, (
        product_name,
        brand,
        description,
        category,
        price,
        quantity,
        unit,
        reorder_level,
        barcode,
        supplier_id
    ))

    conn.commit()
    conn.close()


def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.id,
            products.name,
            products.price,
            products.quantity,
            products.unit,
            products.barcode,
            suppliers.supplier_name
        FROM products
        JOIN suppliers 
        ON products.supplier_id = suppliers.id
    """)

    products = cursor.fetchall()

    conn.close()

    return products


def get_product_by_id(product_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.*,
            suppliers.supplier_name
        FROM products
        LEFT JOIN suppliers
        ON products.supplier_id = suppliers.id
        WHERE products.id = ?
    """, (product_id,))

    product = cursor.fetchone()

    conn.close()

    return product


def update_product(
    product_id,
    product_name,
    brand,
    description,
    category,
    price,
    quantity,
    unit,
    reorder_level,
    supplier_id
):
    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products

        SET
            name = ?,
            brand = ?,
            description = ?,
            category = ?,
            price = ?,
            quantity = ?,
            unit = ?,
            reorder_level = ?,
            supplier_id = ?,
            updated_at = CURRENT_TIMESTAMP

        WHERE id = ?

    """, (
        product_name,
        brand,
        description,
        category,
        price,
        quantity,
        unit,
        reorder_level,
        supplier_id,
        product_id
    ))

    conn.commit()

    conn.close()


def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()


def add_supplier(supplier_name, phone, email):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the supplier already exists
    cursor.execute("""
        SELECT id
        FROM suppliers
        WHERE supplier_name = ?
        AND phone = ?
        AND email = ?
    """, (supplier_name, phone, email))

    existing_supplier = cursor.fetchone()

    if existing_supplier:
        conn.close()
        return False

    cursor.execute("""
        INSERT INTO suppliers (supplier_name, phone, email)
        VALUES (?, ?, ?)
    """, (supplier_name, phone, email))

    conn.commit()
    conn.close()

    return True


def get_all_suppliers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM suppliers")

    suppliers = cursor.fetchall()

    conn.close()

    return suppliers


def get_supplier_by_id(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))

    supplier = cursor.fetchone()

    conn.close()

    return supplier


def update_supplier(supplier_id, supplier_name, phone, email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE suppliers
        SET supplier_name = ?, phone = ?, email = ?
        WHERE id = ?
    """, (supplier_name, phone, email, supplier_id))

    conn.commit()
    conn.close()


def delete_supplier(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))

    conn.commit()
    conn.close()


def add_customer(full_name, phone, email, address):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers (full_name, phone, email, address)
        VALUES (?, ?, ?, ?)
    """, (full_name, phone, email, address))

    conn.commit()
    conn.close()


def get_all_customers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers")

    customers = cursor.fetchall()

    conn.close()

    return customers


def get_customer_by_id(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))

    customer = cursor.fetchone()

    conn.close()

    return customer


def update_customer(customer_id, full_name, phone, email, address):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE customers
        SET full_name = ?, phone = ?, email = ?, address = ?
        WHERE id = ?
    """, (full_name, phone, email, address, customer_id))

    conn.commit()
    conn.close()


def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))

    conn.commit()
    conn.close()


def customer_has_sales(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM sales
        WHERE customer_id = ?
    """, (customer_id,))

    sale = cursor.fetchone()

    conn.close()
    return sale is not None


def get_customer_sales(customer_id):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sales.id,
            products.name,
            sales.quantity,
            sales.sale_date
        FROM sales
        JOIN products
        ON sales.product_id = products.id
        WHERE sales.customer_id = ?
        ORDER BY sales.sale_date DESC
    """, (customer_id,))

    sales = cursor.fetchall()

    conn.close()

    return sales


def process_sale(customer_id, items, user_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # Create the main sale/invoice
        cursor.execute("""
            INSERT INTO sales (
                customer_id,
                product_id,
                quantity,
                total_price,
                user_id
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            customer_id,
            items[0]["product_id"],
            items[0]["quantity"],
            items[0]["total_price"],
            user_id
        ))

        sale_id = cursor.lastrowid

        # Add every product to sale_items
        for item in items:

            cursor.execute("""
                INSERT INTO sale_items (
                    sale_id,
                    product_id,
                    quantity,
                    unit,
                    unit_price,
                    total_price,
                    unit
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_id,
                item["product_id"],
                item["quantity"],
                item["unit"],
                item["unit_price"],
                item["total_price"],
                item["unit"]
            ))

            # Reduce stock
            cursor.execute("""
                UPDATE products
                SET quantity = ?
                WHERE id = ?
            """, (
                item["new_quantity"],
                item["product_id"]
            ))

        conn.commit()

        return sale_id

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()


def get_all_sales(page=1, per_page=5):

    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    cursor.execute("""
        SELECT
            sales.id,

            customers.full_name AS customer_name,

            COALESCE(
                (
                    SELECT GROUP_CONCAT(product_name, char(10))
                    FROM (
                        SELECT products2.name AS product_name
                        FROM sale_items
                        JOIN products AS products2
                        ON sale_items.product_id = products2.id
                        WHERE sale_items.sale_id = sales.id
                        ORDER BY sale_items.id
                    )
                ),
                products.name
            ) AS product_name,


            COALESCE(
                (
                    SELECT GROUP_CONCAT(quantity, char(10))
                    FROM (
                        SELECT sale_items.quantity
                        FROM sale_items
                        WHERE sale_items.sale_id = sales.id
                        ORDER BY sale_items.id
                    )
                ),
                CAST(sales.quantity AS TEXT)
            ) AS quantity,


            COALESCE(
                (
                    SELECT GROUP_CONCAT(unit, char(10))
                    FROM (
                        SELECT
                            COALESCE(
                                NULLIF(sale_items.unit, ''),
                                products2.unit
                            ) AS unit
                        FROM sale_items
                        JOIN products AS products2
                        ON sale_items.product_id = products2.id
                        WHERE sale_items.sale_id = sales.id
                        ORDER BY sale_items.id
                    )
                ),
                products.unit
            ) AS unit,


            COALESCE(
                (
                    SELECT GROUP_CONCAT(unit_price, char(10))
                    FROM (
                        SELECT sale_items.unit_price
                        FROM sale_items
                        WHERE sale_items.sale_id = sales.id
                        ORDER BY sale_items.id
                    )
                ),
                CAST(products.price AS TEXT)
            ) AS unit_price,


            COALESCE(
                (
                    SELECT GROUP_CONCAT(total_price, char(10))
                    FROM (
                        SELECT sale_items.total_price
                        FROM sale_items
                        WHERE sale_items.sale_id = sales.id
                        ORDER BY sale_items.id
                    )
                ),
                CAST(sales.total_price AS TEXT)
            ) AS total_price,


            sales.sale_date

        FROM sales

        JOIN customers
        ON sales.customer_id = customers.id

        JOIN products
        ON sales.product_id = products.id

        ORDER BY sales.sale_date DESC

        LIMIT ?
        OFFSET ?

    """, (per_page, offset))

    sales = cursor.fetchall()

    conn.close()

    return sales


def get_recent_sales():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            customers.full_name AS customer_name,
            products.name AS product_name,
            sales.total_price,
            sales.sale_date

        FROM sales

        JOIN customers
        ON sales.customer_id = customers.id

        JOIN products
        ON sales.product_id = products.id

        ORDER BY sales.sale_date DESC

        LIMIT 5
    """)

    recent_sales = cursor.fetchall()

    conn.close()

    return recent_sales


def get_total_sales_count():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def supplier_has_products(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM products
        WHERE supplier_id = ?
    """, (supplier_id,))

    product = cursor.fetchone()

    conn.close()

    return product is not None


def get_products_by_supplier_id(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.id,
            products.name,
            products.price,
            products.quantity,
            suppliers.supplier_name
        FROM products
        JOIN suppliers
        ON products.supplier_id = suppliers.id
        WHERE products.supplier_id = ?
    """, (supplier_id,))

    products = cursor.fetchall()

    conn.close()

    return products


def search_products(query):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.id,
            products.name,
            products.price,
            products.quantity,
            suppliers.supplier_name
        FROM products
        JOIN suppliers
        ON products.supplier_id = suppliers.id
        WHERE products.name LIKE ?
    """, (f"%{query}%",))

    products = cursor.fetchall()

    conn.close()

    return products


def get_low_stock_products():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.id,
            products.name,
            products.price,
            products.quantity,
            products.unit,
            products.reorder_level,
            suppliers.supplier_name
        FROM products
        JOIN suppliers
        ON products.supplier_id = suppliers.id
        WHERE products.quantity < products.reorder_level
        AND products.quantity > 0
        ORDER BY products.quantity ASC
        LIMIT 5
    """)

    low_stock_products = cursor.fetchall()

    conn.close()

    return low_stock_products


def get_total_products():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM products
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_total_suppliers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
         FROM suppliers
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_total_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM customers
    """)
    
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return total


def get_low_stock_count():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM products 
        WHERE quantity < reorder_level
        AND quantity > 0
    """)

    low_stock_count = cursor.fetchone()[0]

    conn.close()

    return low_stock_count


def get_out_of_stock_count():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) 
        FROM products WHERE quantity = 0
    """)

    out_of_stock_count = cursor.fetchone()[0]

    conn.close()

    return out_of_stock_count


def get_out_of_stock_products():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.id,
            products.name,
            products.price,
            products.quantity,
            suppliers.supplier_name
        FROM products
        JOIN suppliers
        ON products.supplier_id = suppliers.id
        WHERE products.quantity = 0
        ORDER BY products.name ASC
        LIMIT 5
    """)

    out_of_stock_products = cursor.fetchall()

    conn.close()

    return out_of_stock_products


def get_total_revenue():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(sales.total_price)
        FROM sales
    """)

    revenue = cursor.fetchone()[0]
    conn.close()

    return revenue or 0


def get_total_sales():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*)
        FROM sales
    """)

    total_sales = cursor.fetchone()[0]
    conn.close()

    return total_sales or 0


def get_average_sale():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            AVG(total_price)
        FROM sales
    """)

    average_sale = cursor.fetchone()[0]

    conn.close()

    return average_sale or 0


def get_best_selling_products(minimum_sales=None):

    conn = get_db_connection()

    cursor = conn.cursor()

    query = """
        SELECT

            products.name,

            SUM(sales.quantity) AS total_sold,

            SUM(sales.total_price) AS revenue

        FROM sales

        JOIN products

        ON sales.product_id = products.id

        GROUP BY products.name
    """

    # Optional HAVING filter
    if minimum_sales is not None:

        query += """
            HAVING total_sold >= ?
        """

    # Finish the query
    query += """
        ORDER BY total_sold DESC
        LIMIT 5
    """

    if minimum_sales is not None:

        cursor.execute(query, (minimum_sales,))

    else:

        cursor.execute(query)

    products = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return products


def get_products_paginated(limit, offset):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            products.*,
            suppliers.supplier_name

        FROM products

        LEFT JOIN suppliers

        ON products.supplier_id = suppliers.id

        ORDER BY products.id DESC

        LIMIT ?

        OFFSET ?
    """, (limit, offset))

    products = cursor.fetchall()

    conn.close()

    return products


def get_suppliers_paginated(limit, offset):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM suppliers
        ORDER BY id DESC
        LIMIT ?
        OFFSET ?
    """, (limit, offset))

    suppliers = cursor.fetchall()

    conn.close()

    return suppliers


def get_customers_paginated(limit, offset):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            customers.*,
            products.name

        FROM customers

        LEFT JOIN products

        ON customers.id = products.supplier_id

        ORDER BY customers.id DESC

        LIMIT ?

        OFFSET ?
    """, (limit, offset))

    customers = cursor.fetchall()

    conn.close()

    return customers        


def add_purchase(product_id, supplier_id, quantity, purchase_price):

    conn = get_db_connection()

    cursor = conn.cursor()

    # Record the purchase
    cursor.execute("""
        INSERT INTO purchases(
            product_id,
            supplier_id,
            quantity,
            purchase_price
        )
        VALUES(?,?,?,?)
    """, (product_id, supplier_id, quantity, purchase_price))

    # Connect product to supplier
    cursor.execute("""
        INSERT OR IGNORE INTO product_suppliers (
            product_id,
            supplier_id
        )
        VALUES (?, ?)
    """, (product_id, supplier_id))

    # Increase product stock
    cursor.execute("""
        UPDATE products
        SET quantity = quantity + ?
        WHERE id = ?
    """, (quantity, product_id))

    conn.commit()

    conn.close()


def update_purchase(purchase_id, new_quantity, new_purchase_price):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # Get the original purchase
        cursor.execute("""
            SELECT product_id, quantity
            FROM purchases
            WHERE id = ?
        """, (purchase_id,))

        purchase = cursor.fetchone()

        if not purchase:
            return False

        old_quantity = purchase["quantity"]
        product_id = purchase["product_id"]

        # Calculate the difference
        quantity_difference = new_quantity - old_quantity

        # Update the purchase record
        cursor.execute("""
            UPDATE purchases
            SET quantity = ?,
                purchase_price = ?
            WHERE id = ?
        """, (
            new_quantity,
            new_purchase_price,
            purchase_id
        ))

        # Adjust product stock
        cursor.execute("""
            UPDATE products
            SET quantity = quantity + ?
            WHERE id = ?
        """, (
            quantity_difference,
            product_id
        ))

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()



def delete_purchase_record(purchase_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # Get the purchase and current product stock
        cursor.execute("""
            SELECT
                purchases.product_id,
                purchases.quantity,
                products.quantity AS current_stock

            FROM purchases

            JOIN products
            ON purchases.product_id = products.id

            WHERE purchases.id = ?
        """, (purchase_id,))

        purchase = cursor.fetchone()

        if not purchase:
            return False

        product_id = purchase["product_id"]
        purchase_quantity = purchase["quantity"]
        current_stock = purchase["current_stock"]

        # Make sure stock will not become negative
        if current_stock < purchase_quantity:
            return False

        # Remove the purchased quantity from stock
        cursor.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE id = ?
        """, (purchase_quantity, product_id))

        # Delete the purchase record
        cursor.execute("""
            DELETE FROM purchases
            WHERE id = ?
        """, (purchase_id,))

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        raise

    finally:

        conn.close()


def get_all_purchases( page=1, per_page=5):

    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    cursor.execute("""
        SELECT
            purchases.id,
            products.name AS product_name,
            suppliers.supplier_name,
            purchases.quantity,
            products.unit,
            purchases.purchase_price,
            purchases.quantity * purchases.purchase_price AS total_cost,
            purchases.purchase_date

        FROM purchases

        JOIN products
        ON purchases.product_id = products.id

        JOIN suppliers
        ON purchases.supplier_id = suppliers.id

        ORDER BY purchases.purchase_date DESC

        LIMIT ?
        OFFSET ?
    """, (per_page, offset))

    purchases = cursor.fetchall()

    conn.close()

    return purchases


def get_total_purchases():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM purchases
    """)

    total_purchases = cursor.fetchone()[0]

    conn.close()

    return total_purchases


def get_purchase_by_id(purchase_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            purchases.id,
            purchases.product_id,
            purchases.supplier_id,
            purchases.quantity,
            purchases.purchase_price,
            purchases.purchase_date,
            products.name AS product_name,
            products.unit,
            suppliers.supplier_name

        FROM purchases

        JOIN products
        ON purchases.product_id = products.id

        JOIN suppliers
        ON purchases.supplier_id = suppliers.id

        WHERE purchases.id = ?
    """, (purchase_id,))

    purchase = cursor.fetchone()

    conn.close()

    return purchase


def get_sale_by_id(sale_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the main sale information
    cursor.execute("""
        SELECT
            sales.id,
            customers.full_name AS customer_name,
            users.username AS sales_rep,
            sales.total_price,
            sales.sale_date

        FROM sales

        JOIN customers
        ON sales.customer_id = customers.id

        LEFT JOIN users
        ON sales.user_id = users.id

        WHERE sales.id = ?
    """, (sale_id,))

    sale = cursor.fetchone()

    if not sale:
        conn.close()
        return None

    # Get all products belonging to this sale
    cursor.execute("""
        SELECT
            products.name AS product_name,
            COALESCE(NULLIF(sale_items.unit, ''), products.unit) AS unit,
            sale_items.quantity,
            sale_items.unit_price,
            sale_items.total_price

        FROM sale_items

        JOIN products
        ON sale_items.product_id = products.id

        WHERE sale_items.sale_id = ?

        ORDER BY sale_items.id
    """, (sale_id,))

    items = cursor.fetchall()

    # Calculate the grand total
    grand_total = sum(
        item["total_price"] for item in items
    )

    conn.close()

    return {
        "id": sale["id"],
        "customer_name": sale["customer_name"],
        "sales_rep": sale["sales_rep"] or "Unknown",
        "total_price": grand_total,
        "sale_date": sale["sale_date"],
        "items": items
    }


def get_walk_in_customer_id():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM customers
        WHERE full_name = ?
    """, ("Walk-in Customer",))

    customer = cursor.fetchone()

    if customer is None:

        cursor.execute("""
            INSERT INTO customers (full_name)
            VALUES (?)
        """, ("Walk-in Customer",))

        conn.commit()

        customer_id = cursor.lastrowid

    else:

        customer_id = customer["id"]

    conn.close()

    return customer_id


def get_supplier_purchase_summary(product_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            suppliers.supplier_name,
            SUM(purchases.quantity) AS total_quantity,
            SUM(purchases.quantity * purchases.purchase_price) AS total_cost,
            AVG(purchases.purchase_price) AS average_price

        FROM purchases

        JOIN suppliers
        ON purchases.supplier_id = suppliers.id

        WHERE purchases.product_id = ?

        GROUP BY suppliers.id

        ORDER BY total_quantity DESC
    """, (product_id,))

    supplier_summary = cursor.fetchall()

    conn.close()

    return supplier_summary