import os
from datetime import date, timedelta
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

import database
from AdminStorage import admin_storage_bp


app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "FelixPham")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "current_user" not in session:
            flash("Vui lòng đăng nhập để tiếp tục.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = session.get("current_user")
        if not user:
            return redirect(url_for("login", next=request.path))
        if not user.get("is_admin"):
            abort(403)
        return view(*args, **kwargs)
    return wrapped_view


def calculate_cart(cart):
    total_quantity = sum(item["quantity"] for item in cart)
    total_price = sum(item["price"] * item["quantity"] for item in cart)
    return total_quantity, total_price


@app.template_filter("vnd")
def format_vnd(value):
    return f"{float(value):,.0f} ₫".replace(",", ".")


@app.context_processor
def shared_data():
    cart = session.get("cart", [])
    return {
        "cart_count": sum(item.get("quantity", 0) for item in cart),
        "current_user": session.get("current_user"),
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_name = request.form.get("txt_username", "").strip()
        password = request.form.get("txt_password", "")
        user = database.get_user(login_name)
        valid = False
        if user:
            stored = user["password"]
            if stored.startswith(("scrypt:", "pbkdf2:")):
                valid = check_password_hash(stored, password)
            else:
                valid = stored == password
        if not valid:
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", "error")
            return render_template("Login.html"), 401
        session["current_user"] = {
            "id": user["id"], "name": user["name"], "email": user["email"],
            "address": user["address"], "mobile": user["mobile"],
            "is_admin": bool(user["is_admin"]),
        }
        next_url = request.form.get("next", "")
        if not next_url.startswith("/") or next_url.startswith("//"):
            next_url = url_for("index")
        return redirect(next_url)
    return render_template("Login.html", next_url=request.args.get("next", ""))


@app.get("/logout")
def logout():
    session.pop("current_user", None)
    return redirect(url_for("index"))


@app.get("/")
def index():
    return render_template(
        "SearchWithCSSDataDBAddToCart.html", search_text="", products=database.list_products()
    )


@app.route("/searchData", methods=["GET", "POST"])
def search_data():
    search_text = request.values.get("searchInput", "").strip()
    return render_template(
        "SearchWithCSSDataDBAddToCart.html",
        search_text=search_text,
        products=database.list_products(search_text),
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    return search_data()


@app.post("/cart/add")
def add_to_cart():
    product_id = request.form.get("product_id", type=int)
    quantity = request.form.get("quantity", type=int)
    product = database.get_product(product_id) if product_id else None
    if not product or quantity is None or quantity < 1:
        flash("Sản phẩm hoặc số lượng không hợp lệ.", "error")
        return redirect(request.referrer or url_for("index"))
    if quantity > product["stock"]:
        flash("Số lượng vượt quá tồn kho.", "error")
        return redirect(request.referrer or url_for("index"))

    cart = session.get("cart", [])
    for item in cart:
        if item["id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart.append({
            "id": product["id"], "name": product["model"],
            "price": float(product["price"]), "quantity": quantity,
            "picture": product["picture"], "details": product["details"],
        })
    session["cart"] = cart
    flash("Product added to cart successfully!", "success")
    return redirect(request.referrer or url_for("view_cart"))


@app.route("/cart", methods=["GET", "POST"])
@app.route("/view_cart", methods=["GET", "POST"])
def view_cart():
    cart = session.get("cart", [])
    total_quantity, total_price = calculate_cart(cart)
    return render_template("cart.html", carts=cart, total_quantity=total_quantity, total_price=total_price)


@app.post("/cart/update/<int:product_id>")
def update_cart(product_id):
    quantity = request.form.get(f"quantity_{product_id}", type=int)
    cart = session.get("cart", [])
    for item in cart:
        if item["id"] == product_id:
            if not quantity or quantity <= 0:
                cart.remove(item)
            else:
                item["quantity"] = quantity
            break
    session["cart"] = cart
    return redirect(url_for("view_cart"))


@app.post("/update_cart")
@app.post("/update_cart_v1")
@app.post("/update_cart_v2")
@app.post("/cart/update-v2")
def update_cart_v2():
    new_cart = []
    for item in session.get("cart", []):
        product_id = str(item["id"])
        quantity = request.form.get(f"quantity_{product_id}", type=int)
        if quantity is None:
            quantity = request.form.get(f"quantity-{product_id}", item["quantity"], type=int)
        if quantity and quantity > 0 and f"delete-{product_id}" not in request.form:
            item["quantity"] = quantity
            new_cart.append(item)
    session["cart"] = new_cart
    return redirect(url_for("view_cart"))


@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    session["cart"] = [item for item in session.get("cart", []) if item["id"] != product_id]
    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET", "POST"])
@app.post("/proceed_cart")
@login_required
def checkout():
    cart = session.get("cart", [])
    if not cart:
        return redirect(url_for("view_cart"))
    _, total_price = calculate_cart(cart)
    user = session["current_user"]
    if request.method == "GET":
        return render_template("checkout.html", carts=cart, total_price=total_price, user=user)
    customer = {
        "name": request.form.get("customer_name", user["name"]).strip(),
        "email": request.form.get("customer_email", user["email"]).strip(),
        "mobile": request.form.get("customer_mobile", user["mobile"]).strip(),
        "address": request.form.get("customer_address", user["address"]).strip(),
        "payment_method": request.form.get("payment_method", "COD").strip(),
    }
    try:
        order_id = database.create_order(
            user, customer, cart, total_price, date.today() + timedelta(days=5)
        )
    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("view_cart"))
    session["cart"] = []
    return redirect(url_for("view_order", order_id=order_id))


@app.get("/orders")
@login_required
def view_orders():
    return render_template(
        "orders.html", orders=database.list_orders_for_user(session["current_user"]["id"])
    )


@app.get("/orders/<int:order_id>")
@login_required
def view_order(order_id):
    user = session["current_user"]
    order = database.get_order(order_id, None if user.get("is_admin") else user["id"])
    if not order:
        abort(404)
    return render_template(
        "order_detail.html", order=order, items=database.get_order_details(order_id)
    )


@app.get("/admin")
@admin_required
def admin():
    products, orders, statistics = database.get_admin_summary()
    return render_template(
        "admin.html", products=products, orders=orders, statistics=statistics
    )


app.register_blueprint(admin_storage_bp)


if __name__ == "__main__":
    app.run(debug=True)
