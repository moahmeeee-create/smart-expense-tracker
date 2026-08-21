from flask import jsonify, Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-before-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///smart_expense.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    incomes = db.relationship(
        "Income",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    expenses = db.relationship(
        "Expense",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )



class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("من فضلك املأ جميع البيانات", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("كلمتا المرور غير متطابقتين", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("كلمة المرور يجب أن تكون 6 أحرف على الأقل", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(username=username).first():
            flash("اسم المستخدم موجود بالفعل", "error")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("البريد الإلكتروني مستخدم بالفعل", "error")
            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash("تم إنشاء الحساب بنجاح، سجل دخولك الآن", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username_or_email = request.form.get(
            "username_or_email",
            ""
        ).strip()

        password = request.form.get("password", "")

        user = User.query.filter(
            (User.username == username_or_email)
            |
            (User.email == username_or_email.lower())
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):
            session["user_id"] = user.id
            flash("تم تسجيل الدخول بنجاح", "success")
            return redirect(url_for("dashboard"))

        flash("اسم المستخدم أو كلمة المرور غير صحيحة", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("تم تسجيل الخروج", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():

    user = db.session.get(User, session["user_id"])

    total_income = sum(
        item.amount for item in user.incomes
    )

    total_expenses = sum(
        item.amount for item in user.expenses
    )

    balance = total_income - total_expenses

    finance_total = total_income + total_expenses

    income_percentage = (
        total_income / finance_total * 100
        if finance_total > 0 else 0
    )

    expense_percentage = (
        total_expenses / finance_total * 100
        if finance_total > 0 else 0
    )

    category_totals = {}

    for item in user.expenses:
        category_totals[item.category] = (
            category_totals.get(item.category, 0)
            + item.amount
        )

    transactions = []

    for item in user.incomes:
        transactions.append({
            "id": item.id,
            "type": "income",
            "amount": item.amount,
            "description": item.description,
            "category": "دخل",
            "date": item.date
        })

    for item in user.expenses:
        transactions.append({
            "id": item.id,
            "type": "expense",
            "amount": item.amount,
            "description": item.description,
            "category": item.category,
            "date": item.date
        })

    recent_transactions = sorted(
        transactions,
        key=lambda item: item["date"],
        reverse=True
    )[:5]

    return render_template(
        "dashboard.html",
        user=user,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        income_percentage=income_percentage,
        expense_percentage=expense_percentage,
        category_labels=list(category_totals.keys()),
        category_values=list(category_totals.values()),
        recent_transactions=recent_transactions
    )


@app.route("/income", methods=["GET", "POST"])
@login_required
def income():

    if request.method == "POST":

        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        description = request.form.get(
            "description",
            ""
        ).strip()

        if amount <= 0:
            flash("أدخل مبلغًا صحيحًا", "error")
            return redirect(url_for("income"))

        if not description:
            flash("اكتب وصفًا للدخل", "error")
            return redirect(url_for("income"))

        item = Income(
            amount=amount,
            description=description,
            user_id=session["user_id"]
        )

        db.session.add(item)
        db.session.commit()

        flash("تمت إضافة الدخل بنجاح", "success")
        return redirect(url_for("dashboard"))

    return render_template("income.html")


@app.route("/expense", methods=["GET", "POST"])
@login_required
def expense():

    categories = [
        "طعام",
        "مواصلات",
        "فواتير",
        "تسوق",
        "تعليم",
        "ترفيه",
        "صحة",
        "أخرى"
    ]

    if request.method == "POST":

        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        description = request.form.get(
            "description",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        if amount <= 0:
            flash("أدخل مبلغًا صحيحًا", "error")
            return redirect(url_for("expense"))

        if not description or not category:
            flash("أكمل جميع البيانات", "error")
            return redirect(url_for("expense"))

        item = Expense(
            amount=amount,
            description=description,
            category=category,
            user_id=session["user_id"]
        )

        db.session.add(item)
        db.session.commit()

        flash("تمت إضافة المصروف بنجاح", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "expense.html",
        categories=categories
    )


@app.route("/transactions")
@login_required
def transactions():

    user = db.session.get(User, session["user_id"])

    search = request.args.get(
        "search",
        ""
    ).strip()

    transaction_type = request.args.get(
        "type",
        "all"
    )

    items = []

    if transaction_type in ("all", "income"):
        for item in user.incomes:
            items.append({
                "id": item.id,
                "type": "income",
                "amount": item.amount,
                "description": item.description,
                "category": "دخل",
                "date": item.date
            })

    if transaction_type in ("all", "expense"):
        for item in user.expenses:
            items.append({
                "id": item.id,
                "type": "expense",
                "amount": item.amount,
                "description": item.description,
                "category": item.category,
                "date": item.date
            })

    if search:
        search_lower = search.lower()

        items = [
            item for item in items
            if search_lower in item["description"].lower()
            or search_lower in item["category"].lower()
        ]

    items.sort(
        key=lambda item: item["date"],
        reverse=True
    )

    return render_template(
        "transactions.html",
        transactions=items,
        search=search,
        transaction_type=transaction_type
    )


@app.route("/income/delete/<int:item_id>")
@login_required
def delete_income(item_id):

    item = Income.query.filter_by(
        id=item_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()

    flash("تم حذف الدخل", "success")
    return redirect(url_for("transactions"))


@app.route("/expense/delete/<int:item_id>")
@login_required
def delete_expense(item_id):

    item = Expense.query.filter_by(
        id=item_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()

    flash("تم حذف المصروف", "success")
    return redirect(url_for("transactions"))


with app.app_context():
    db.create_all()


@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    user_id = session["user_id"]
    current_month = datetime.now().strftime("%Y-%m")

    categories = [
        "طعام",
        "مواصلات",
        "فواتير",
        "تسوق",
        "تعليم",
        "ترفيه",
        "صحة",
        "أخرى"
    ]

    if request.method == "POST":
        category = request.form.get("category", "").strip()

        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        if category not in categories:
            flash("اختر تصنيفًا صحيحًا", "error")
            return redirect(url_for("budget"))

        if amount <= 0:
            flash("أدخل ميزانية صحيحة", "error")
            return redirect(url_for("budget"))

        existing = Budget.query.filter_by(
            category=category,
            month=current_month,
            user_id=user_id
        ).first()

        if existing:
            existing.amount = amount
        else:
            db.session.add(Budget(
                category=category,
                amount=amount,
                month=current_month,
                user_id=user_id
            ))

        db.session.commit()
        flash("تم حفظ الميزانية بنجاح", "success")
        return redirect(url_for("budget"))

    budgets = Budget.query.filter_by(
        month=current_month,
        user_id=user_id
    ).all()

    expenses = Expense.query.filter_by(user_id=user_id).all()

    budget_data = []

    for item in budgets:
        spent = sum(
            expense.amount
            for expense in expenses
            if expense.category == item.category
            and expense.date.strftime("%Y-%m") == current_month
        )

        remaining = item.amount - spent
        percentage = (spent / item.amount * 100) if item.amount else 0

        budget_data.append({
            "id": item.id,
            "category": item.category,
            "amount": item.amount,
            "spent": spent,
            "remaining": remaining,
            "percentage": min(percentage, 100)
        })

    return render_template(
        "budget.html",
        categories=categories,
        budget_data=budget_data,
        current_month=current_month
    )


@app.route("/budget/delete/<int:item_id>")
@login_required
def delete_budget(item_id):
    item = Budget.query.filter_by(
        id=item_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()

    flash("تم حذف الميزانية", "success")
    return redirect(url_for("budget"))

@app.route("/api/transactions")
@login_required
def api_transactions():
    user_id = session["user_id"]
    search = request.args.get("search", "").strip().lower()
    transaction_type = request.args.get("type", "all")
    items = []

    if transaction_type in ("all", "income"):
        for item in Income.query.filter_by(user_id=user_id).all():
            items.append({
                "id": item.id,
                "type": "income",
                "amount": item.amount,
                "description": item.description,
                "category": "دخل",
                "date": item.date.isoformat()
            })

    if transaction_type in ("all", "expense"):
        for item in Expense.query.filter_by(user_id=user_id).all():
            items.append({
                "id": item.id,
                "type": "expense",
                "amount": item.amount,
                "description": item.description,
                "category": item.category,
                "date": item.date.isoformat()
            })

    if search:
        items = [
            item for item in items
            if search in item["description"].lower()
            or search in item["category"].lower()
        ]

    items.sort(key=lambda item: item["date"], reverse=True)

    return jsonify({
        "success": True,
        "count": len(items),
        "transactions": items
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG", "0") == "1"
    )
