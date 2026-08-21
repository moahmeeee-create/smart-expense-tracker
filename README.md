# 💰 Smart Expense Tracker

A full-stack personal expense tracking application built with **Python, Flask, SQLAlchemy, HTML, CSS, and JavaScript**.

Smart Expense Tracker helps users manage income and expenses, monitor their balance, organize transactions, set monthly budgets, and export financial data.

## ✨ Features

- 🔐 User registration and login
- 💵 Add and manage income
- 💸 Add and manage expenses
- 📊 Dashboard with financial summaries and charts
- 💰 Automatic balance calculation
- 🏷️ Expense categories
- 🔎 Search and filter transactions
- 👤 User-specific transaction data
- 🔒 User data isolation
- 🗑️ Delete income and expenses
- 💰 Monthly budget management
- 📥 Export transactions to CSV
- 📄 Export transactions to PDF
- 🌐 JSON API for transactions
- 🧪 Automated tests with pytest
- ⚙️ GitHub Actions CI
- 📱 Responsive interface

## 🛠️ Tech Stack

### Backend
- Python 3.13
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- ReportLab

### Frontend
- HTML5
- CSS3
- JavaScript
- Chart.js

### Database
- SQLite

### Testing
- pytest

### Deployment
- Gunicorn
- GitHub Actions

## 📊 Dashboard

The dashboard provides:

- Total income
- Total expenses
- Current balance
- Expense summaries
- Recent transactions
- Visual charts

## 🔎 Search & Filtering

Transactions can be filtered by:

- Transaction type
- Search text
- Description
- Category

## 📥 CSV & 📄 PDF Export

Authenticated users can export their transaction data:

```text
GET /export/csv
GET /export/pdf

