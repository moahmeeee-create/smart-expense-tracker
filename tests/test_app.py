import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            from app import db
            db.create_all()

        yield client

        with app.app_context():
            from app import db
            db.drop_all()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code in (200, 302)


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_protected_transactions(client):
    response = client.get("/transactions")
    assert response.status_code == 302


def test_protected_budget(client):
    response = client.get("/budget")
    assert response.status_code == 302


def test_register_and_login(client):
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456",
            "confirm_password": "123456",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    response = client.post(
        "/login",
        data={
            "username_or_email": "testuser",
            "password": "123456",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_transactions_api_requires_login(client):
    response = client.get("/api/transactions")
    assert response.status_code in (302, 401)


def test_add_income_and_expense(client):
    client.post(
        "/register",
        data={
            "username": "financeuser",
            "email": "finance@example.com",
            "password": "123456",
            "confirm_password": "123456",
        },
    )

    client.post(
        "/login",
        data={
            "username_or_email": "financeuser",
            "password": "123456",
        },
    )

    income_response = client.post(
        "/income",
        data={
            "amount": "10000",
            "description": "Salary",
        },
    )
    assert income_response.status_code == 302

    expense_response = client.post(
        "/expense",
        data={
            "amount": "150",
            "description": "غداء",
            "category": "طعام",
        },
    )
    assert expense_response.status_code == 302


def test_transactions_api_returns_added_data(client):
    client.post(
        "/register",
        data={
            "username": "apiuser",
            "email": "api@example.com",
            "password": "123456",
            "confirm_password": "123456",
        },
    )

    client.post(
        "/login",
        data={
            "username_or_email": "apiuser",
            "password": "123456",
        },
    )

    client.post(
        "/income",
        data={
            "amount": "10000",
            "description": "Salary",
        },
    )

    client.post(
        "/expense",
        data={
            "amount": "250",
            "description": "غداء",
            "category": "طعام",
        },
    )

    response = client.get("/api/transactions")

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 2
    assert any(
        item["type"] == "income" and item["amount"] == 10000
        for item in data["transactions"]
    )
    assert any(
        item["type"] == "expense" and item["amount"] == 250
        for item in data["transactions"]
    )


def test_dashboard_balance(client):
    client.post(
        "/register",
        data={
            "username": "balanceuser",
            "email": "balance@example.com",
            "password": "123456",
            "confirm_password": "123456",
        },
    )

    client.post(
        "/login",
        data={
            "username_or_email": "balanceuser",
            "password": "123456",
        },
    )

    client.post(
        "/income",
        data={
            "amount": "10000",
            "description": "Salary",
        },
    )

    client.post(
        "/expense",
        data={
            "amount": "1500",
            "description": "Shopping",
            "category": "تسوق",
        },
    )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"8,500.00" in response.data
def test_user_isolation(client):
    # إنشاء المستخدم الأول
    client.post(
        "/register",
        data={
            "username": "userone",
            "email": "one@example.com",
            "password": "123456",
            "confirm_password": "123456",
        },
    )

    client.post(
        "/login",
        data={
            "username_or_email": "userone",
            "password": "123456",
        },
    )

    client.post(
        "/income",
        data={
            "amount": "5000",
            "description": "User One Salary",
        },
    )

    client.get("/logout")

    # إنشاء المستخدم الثاني
    client.post(
        "/register",
        data={
            "username": "usertwo",
            "email": "two@example.com",
            "password": "123456",
            "confirm_password": "123456",
        },
    )

    client.post(
        "/login",
        data={
            "username_or_email": "usertwo",
            "password": "123456",
        },
    )

    response = client.get("/api/transactions")

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 0
def test_delete_expense(client):
    client.post(
        "/register",
        data={
            "username": "deleteuser",
            "email": "delete@example.com",
            "password": "123456",
            "confirm_password": "123456",
        },
    )

    client.post(
        "/login",
        data={
            "username_or_email": "deleteuser",
            "password": "123456",
        },
    )

    response = client.post(
        "/expense",
        data={
            "amount": "200",
            "description": "Test Expense",
            "category": "طعام",
        },
    )
    assert response.status_code == 302

    response = client.get("/api/transactions")
    data = response.get_json()

    assert data["count"] == 1
    expense_id = data["transactions"][0]["id"]

    response = client.get(f"/expense/delete/{expense_id}")
    assert response.status_code == 302

    response = client.get("/api/transactions")
    data = response.get_json()

    assert data["count"] == 0
