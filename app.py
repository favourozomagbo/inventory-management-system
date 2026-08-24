from itertools import product
import math
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A5
from flask import send_file
import io
import re
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import (
    create_tables,

    add_product,get_all_products,get_product_by_id,

    get_total_sales_count,update_product,delete_product, get_products_paginated,

    add_supplier,get_all_suppliers,get_supplier_by_id,update_supplier,delete_supplier,get_suppliers_paginated,

    supplier_has_products,get_products_by_supplier_id, search_products,

    get_low_stock_products,get_total_products,get_total_suppliers,get_low_stock_count,

    add_customer,get_all_customers,get_customer_by_id,update_customer,delete_customer,customer_has_sales, get_customers_paginated,

    get_total_customers, get_customer_sales, get_recent_sales,

    process_sale,get_all_sales, get_total_revenue, get_total_sales, get_average_sale, get_best_selling_products,

    get_out_of_stock_count, get_out_of_stock_products, add_purchase, get_all_purchases, get_total_purchases, get_sale_by_id,

    add_user, get_user_by_email, get_walk_in_customer_id, get_supplier_purchase_summary, update_purchase, get_purchase_by_id,

    delete_purchase_record)

app = Flask(__name__)

app.secret_key = "inventory_management_secret_key_2026"


def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""


@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        existing_user = get_user_by_email(email)

        if existing_user:

            flash("An account with this email already exists.", "warning")

            return redirect(url_for("signup"))

        valid, message = is_strong_password(password)

        if not valid:

            flash(message, "danger")

            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        add_user(username, email, hashed_password)

        flash("Account created successfully! Please log in.", "success")

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip()
        password = request.form["password"]

        user = get_user_by_email(email)

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash("Login successful.", "success")

            return redirect(url_for("home"))
        else:
            flash("Invalid email or password, please try again.", "danger")

    return render_template("login.html")


@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "POST":

        product_name = request.form["product_name"].strip()

        brand = request.form["brand"].strip()

        description = request.form["description"].strip()

        category = request.form["category"].strip()

        price = float(request.form["price"])

        quantity = int(request.form["quantity"])

        unit = request.form["unit"].strip()

        reorder_level = int(request.form["reorder_level"])

        supplier_id = int(request.form["supplier_id"])


        add_product(
        product_name,
        brand,
        description,
        category,
        price,
        quantity,
        unit,
        reorder_level,
        supplier_id
    )
        flash("Product added successfully!", "success")
        return redirect(url_for("products"))

    
    page = request.args.get("page", 1, type=int)
    page_size = 5
    offset = (page - 1) * page_size

    total_products = get_total_products()
    total_pages = max(1, math.ceil(total_products / page_size))
    products = get_products_paginated(page_size, offset)
    suppliers = get_all_suppliers()


    return render_template(
        "products.html", 
        products=products, 
        suppliers=suppliers, 
        page=page, 
        total_pages=total_pages
    )


@app.route("/products/<int:product_id>/details")
def product_details(product_id):

    product = get_product_by_id(product_id)

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))

    supplier_summary = get_supplier_purchase_summary(product_id)

    return render_template(
        "product_details.html",
        product=product,
        supplier_summary=supplier_summary
    )


@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def edit_product(product_id):

    product = get_product_by_id(product_id)

    if product is None:
        return "Product not found", 404

    if request.method == "POST":

        product_name = request.form["product_name"].strip()

        brand = request.form["brand"].strip()

        description = request.form["description"].strip()

        category = request.form["category"].strip()

        price = float(request.form["price"])

        quantity = int(request.form["quantity"])

        unit = request.form["unit"].strip()

        reorder_level = int(request.form["reorder_level"])

        supplier_id = int(request.form["supplier_id"])

        update_product(
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
        )

        flash("Product updated successfully!", "success")

        return redirect(url_for("products"))

    suppliers = get_all_suppliers()

    return render_template(
        "edit_product.html",
        product=product,
        suppliers=suppliers
    )


@app.route("/products/<int:product_id>/delete", methods=["POST"])
def delete_product_route(product_id):
    product = get_product_by_id(product_id)

    if product is None:
        return "Product not found", 404

    delete_product(product_id)

    return redirect(url_for("products"))


@app.route("/suppliers", methods=["GET", "POST"])
@login_required
def suppliers():

    if request.method == "POST":

        supplier_name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip()

        supplier_added = add_supplier(
            supplier_name,
            phone,
            email
        )

        if supplier_added:
            flash("Supplier added successfully.", "success")
        else:
            flash(
                "This supplier already exists.",
                "danger"
            )

        return redirect(url_for("suppliers"))

    page = request.args.get("page", 1, type=int)

    per_page = 5

    offset = (page - 1) * per_page

    suppliers = get_suppliers_paginated(
        limit=per_page,
        offset=offset
    )

    total_suppliers = get_total_suppliers()

    total_pages = math.ceil(
        total_suppliers / per_page
    )

    return render_template(
        "suppliers.html",
        suppliers=suppliers,
        page=page,
        total_pages=total_pages
    )


@app.route("/suppliers/<int:supplier_id>")
def supplier_detail(supplier_id):
    supplier = get_supplier_by_id(supplier_id)

    if supplier is None:
        return "Supplier not found", 404
    
    products = get_products_by_supplier_id(supplier_id)

    return render_template(
        "supplier_detail.html",
          supplier=supplier,
          products=products
    )


@app.route("/suppliers/<int:supplier_id>/edit", methods=["GET", "POST"])
def edit_supplier(supplier_id):

    supplier = get_supplier_by_id(supplier_id)

    if supplier is None:
        return "Supplier not found", 404

    if request.method == "POST":
        supplier_name = request.form["supplier_name"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip()

        update_supplier(supplier_id, supplier_name, phone, email)

        return redirect(url_for("suppliers"))

    return render_template("edit_supplier.html", supplier=supplier)


@app.route("/suppliers/<int:supplier_id>/delete", methods=["POST"])
def delete_supplier_route(supplier_id):

    if supplier_has_products(supplier_id):
        return "Cannot delete supplier because products are linked to it."

    delete_supplier(supplier_id)

    return redirect(url_for("suppliers"))


@app.route("/suppliers/<int:supplier_id>/products")
def supplier_products(supplier_id):

    supplier = get_supplier_by_id(supplier_id)
    if supplier is None:
        return "Supplier not found", 404

    products = get_products_by_supplier_id(supplier_id)

    return render_template(
        "supplier_products.html", 
        supplier=supplier, 
        products=products
    )


@app.route("/customers", methods=["GET", "POST"])
@login_required
def customers():

    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip()
        address = request.form["address"].strip()

        add_customer(full_name, phone, email, address)

        return redirect(url_for("customers"))

    page = request.args.get("page", 1, type=int)
    
    per_page = 5
    
    offset = (page - 1) * per_page

    customers = get_customers_paginated(limit=per_page, offset=offset)

    total_customers = get_total_customers()

    print("Total Customers:", total_customers)

    total_pages = math.ceil(total_customers / per_page)

    return render_template(
        "customers.html",
        customers=customers,
        page=page,
        total_pages=total_pages,
        total_customers=total_customers
    )


@app.route("/customers/<int:customer_id>")
def customer_detail(customer_id):

    customer = get_customer_by_id(customer_id)

    if customer is None:
        return "Customer not found", 404

    sales = get_customer_sales(customer_id)

    return render_template("customer_detail.html", customer=customer, sales=sales)


@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
def edit_customer(customer_id):

    customer = get_customer_by_id(customer_id)

    if customer is None:
        return "Customer not found", 404

    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip()
        address = request.form["address"].strip()

        update_customer(customer_id, full_name, phone, email, address)

        return redirect(url_for("customers"))

    return render_template("edit_customer.html", customer=customer)


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
def delete_customer_route(customer_id):

    if customer_has_sales(customer_id):
        return "Cannot delete customer because sales are linked to this customer."

    delete_customer(customer_id)

    return redirect(url_for("customers"))


@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():

    if request.method == "POST":

        customer_id = request.form.get("customer_id")

        if customer_id:
            customer_id = int(customer_id)
        else:
            customer_id = get_walk_in_customer_id()


        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")


        if not product_ids or not quantities:
            return "Please add at least one product."


        if len(product_ids) != len(quantities):
            return "Product and quantity data do not match."


        items = []


        for product_id, quantity in zip(product_ids, quantities):

            product_id = int(product_id)
            quantity = int(quantity)


            if quantity <= 0:
                return "Quantity must be greater than 0."


            product = get_product_by_id(product_id)


            if product is None:
                return "Product not found", 404


            if quantity > product["quantity"]:
                return (
                    f"Not enough stock available for "
                    f"{product['name']}."
                )


            unit_price = product["price"]

            total_price = unit_price * quantity

            new_quantity = product["quantity"] - quantity


            items.append({
                "product_id": product_id,
                "quantity": quantity,
                "unit": product["unit"],
                "unit_price": unit_price,
                "total_price": total_price,
                "new_quantity": new_quantity
            })


        user_id = session["user_id"]


        process_sale(
            customer_id,
            items,
            user_id
        )


        return redirect(url_for("sales"))


    page = request.args.get("page", 1, type=int)

    per_page = 5

    customers = get_all_customers()

    products = get_all_products()

    sales = get_all_sales(page, per_page)

    total_sales = get_total_sales_count()

    total_pages = (total_sales + per_page - 1) // per_page


    return render_template(
        "sales.html",
        customers=customers,
        products=products,
        sales=sales,
        page=page,
        total_pages=total_pages
    )


@app.route("/search")
def search():

    query = request.args.get("query", "")

    products = search_products(query)

    return render_template(
        "search_results.html",
        products=products,
        query=query)


@app.route("/low_stock")
def low_stock():
    products = get_low_stock_products()
    low_stock_count = get_low_stock_count()

    return render_template(
        "low_stock.html", 
        products=products, 
        low_stock_count=low_stock_count
    )


@app.route("/dashboard")
@login_required
def dashboard():
    total_products = get_total_products()
    total_suppliers = get_total_suppliers()
    low_stock_count = get_low_stock_count()
    out_of_stock_count = get_out_of_stock_count()
    out_of_stock_products = get_out_of_stock_products()
    total_revenue = get_total_revenue()
    total_sales = get_total_sales()
    low_stock_products = get_low_stock_products()

    recent_sales = get_recent_sales()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_suppliers=total_suppliers,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        out_of_stock_products=out_of_stock_products, 
        total_revenue=f"₦{total_revenue:,.2f}",
        total_sales=total_sales,
        recent_sales=recent_sales,
        low_stock_products=low_stock_products 
    )


@app.route("/reports")
@login_required
def reports():

    total_revenue = get_total_revenue()

    total_sales = get_total_sales()

    average_sale = get_average_sale()

    minimum_sales = request.args.get("minimum_sales")
    
    if minimum_sales:
        minimum_sales = int(minimum_sales)
    else:
         minimum_sales = None

    best_selling_products = get_best_selling_products(minimum_sales)


    return render_template(

        "reports.html",

        total_revenue=total_revenue,

        total_sales=total_sales,

        average_sale=average_sale,

        minimum_sales=minimum_sales,

        best_selling_products=best_selling_products,

    )


@app.route("/purchases", methods=["GET", "POST"])
@login_required
def purchases():

    if request.method == "POST":

        product_id = request.form["product_id"]
        supplier_id = request.form["supplier_id"]
        quantity = int(request.form["quantity"])
        purchase_price = float(request.form["purchase_price"])

        add_purchase(
            product_id,
            supplier_id,
            quantity,
            purchase_price
        )

        return redirect(url_for("purchase_history"))

    products = get_all_products()
    suppliers = get_all_suppliers()

    return render_template(
        "purchases.html",
        products=products,
        suppliers=suppliers
    )


@app.route("/purchase-history")
@login_required
def purchase_history():

    page = request.args.get("page", 1, type=int)

    page_size = 5

    purchases = get_all_purchases(page, page_size)

    total_purchases = get_total_purchases()

    total_pages = max(1, math.ceil(total_purchases / page_size))

    return render_template(
        "purchase_history.html",
        purchases=purchases,
        page=page,
        total_pages=total_pages
    )


@app.route("/purchases/<int:purchase_id>/edit", methods=["GET", "POST"])
@login_required
def edit_purchase(purchase_id):

    purchase = get_purchase_by_id(purchase_id)

    if not purchase:
        return "Purchase not found.", 404

    if request.method == "POST":

        quantity = int(request.form["quantity"])
        purchase_price = float(request.form["purchase_price"])

        if quantity <= 0:
            return "Quantity must be greater than 0."

        update_purchase(
            purchase_id,
            quantity,
            purchase_price
        )

        flash("Purchase updated successfully.", "success")

        return redirect(url_for("purchase_history"))

    return render_template(
        "edit_purchase.html",
        purchase=purchase
    )


@app.route("/purchases/<int:purchase_id>/delete", methods=["POST"])
@login_required
def delete_purchase(purchase_id):

    deleted = delete_purchase_record(purchase_id)

    if not deleted:
        flash(
            "Cannot delete this purchase because the available stock is less than the purchased quantity.",
            "error"
        )

        return redirect(url_for("purchase_history"))

    flash("Purchase deleted successfully.", "success")

    return redirect(url_for("purchase_history"))



@app.route("/invoice/<int:sale_id>")
@login_required
def generate_invoice(sale_id):

    sale = get_sale_by_id(sale_id)

    if not sale:
        return "Sale not found.", 404

    pdf_buffer = io.BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A5,
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=8
    )

    company_style = ParagraphStyle(
        "CompanyStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.grey,
        fontSize=8,
        leading=11,
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#2563eb"),
        fontSize=15,
        spaceAfter=10
    )

    thank_you_style = ParagraphStyle(
        "ThankYouStyle",
        parent=styles["Heading3"],
        alignment=TA_CENTER,
        textColor=colors.green,
        fontSize=10,
        spaceBefore=10
    )

    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.grey
    )

    elements = []

    # Company name
    elements.append(
        Paragraph(
            "FavourNova Supplies",
            title_style
        )
    )

    elements.append(
        Paragraph(
            """
            Abuja, Nigeria<br/>
            Email: favour.ozomagbo@gmail.com<br/>
            Phone: +234 814 267 3467
            """,
            company_style
        )
    )

    # Invoice heading
    elements.append(
        Paragraph(
            "SALES INVOICE",
            heading_style
        )
    )

    customer_name = sale["customer_name"] or "Walk-in Customer"

    # Invoice information
    invoice_data = [
        ["Invoice Number", f"INV-{sale['id']:04d}"],
        ["Customer", customer_name],
        ["Sales Representative", sale["sales_rep"]],
        ["Date", sale["sale_date"]]
    ]

    invoice_table = Table(
        invoice_data,
        colWidths=[125, 244]
    )

    invoice_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1),
             colors.HexColor("#1f2937")),

            ("TEXTCOLOR", (0, 0), (0, -1),
             colors.white),

            ("BACKGROUND", (1, 0), (1, -1),
             colors.whitesmoke),

            ("GRID", (0, 0), (-1, -1),
             0.7, colors.HexColor("#2563eb")),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),

            ("TOPPADDING", (0, 0), (-1, -1), 7),

            ("FONTNAME", (0, 0), (0, -1),
             "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ])
    )

    elements.append(invoice_table)

    elements.append(Spacer(1, 12))

    # Products table
    products_data = [
        [
            "Product",
            "Qty",
            "Unit",
            "Unit Price",
            "Total"
        ]
    ]

    for item in sale["items"]:

        products_data.append([
            item["product_name"],
            item["quantity"],
            item["unit"],
            f"NGN {item['unit_price']:,.2f}",
            f"NGN {item['total_price']:,.2f}"
        ])

    products_table = Table(
        products_data,
        colWidths=[115, 45, 45, 80, 84]
    )

    products_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#1f2937")),

            ("TEXTCOLOR", (0, 0), (-1, 0),
             colors.white),

            ("FONTNAME", (0, 0), (-1, 0),
             "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 7.5),

            ("GRID", (0, 0), (-1, -1),
             0.7, colors.HexColor("#2563eb")),

            ("BACKGROUND", (0, 1), (-1, -1),
             colors.whitesmoke),

            ("TEXTCOLOR", (0, 1), (-1, -1),
             colors.black),

            ("ALIGN", (1, 1), (2, -1),
             "CENTER"),

            ("ALIGN", (3, 1), (-1, -1),
             "RIGHT"),

            ("TOPPADDING", (0, 0), (-1, -1), 6),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )

    elements.append(products_table)

    elements.append(Spacer(1, 12))

    # Grand total
    total_data = [
        [
            "GRAND TOTAL",
            f"NGN {sale['total_price']:,.2f}"
        ]
    ]

    total_table = Table(
        total_data,
        colWidths=[220, 149]
    )

    total_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, 0),
             colors.HexColor("#1f2937")),

            ("TEXTCOLOR", (0, 0), (0, 0),
             colors.white),

            ("FONTNAME", (0, 0), (-1, -1),
             "Helvetica-Bold"),

            ("FONTSIZE", (0, 0), (-1, -1), 10),

            ("ALIGN", (1, 0), (1, 0),
             "RIGHT"),

            ("TOPPADDING", (0, 0), (-1, -1), 8),

            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

            ("GRID", (0, 0), (-1, -1),
             0.7, colors.HexColor("#2563eb")),
        ])
    )

    elements.append(total_table)

    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "Thank you for your purchase!",
            thank_you_style
        )
    )

    elements.append(Spacer(1, 6))

    elements.append(
        Paragraph(
            "Generated by FavourNova Supplies. Thank you for your patronage.",
            footer_style
        )
    )

    document.build(elements)

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"Invoice_{sale['id']}.pdf",
        mimetype="application/pdf"
    )


@app.route("/about")
@login_required
def about():
    return render_template("about.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    create_tables()
    app.run(debug=True)