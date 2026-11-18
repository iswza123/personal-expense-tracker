
# Personal Expense Tracker

A web-based Personal Expense Tracker built using Python and Django. This application helps users manage their income and expenses, monitor monthly spending, and maintain personal budgets.

## Features

- User registration, login and logout
- Separate accounts for individual users
- Add, edit and delete transactions
- Track income and expenses
- Categorize financial transactions
- Search transactions by title
- Filter by transaction type, category and date
- Monthly financial reports
- Dashboard charts for income and expenses
- Category-wise expense chart
- Export transactions to CSV
- Set and update monthly budgets
- Track remaining budget
- Overspending warnings with progress indicators
- User-specific transaction and budget records

## Technologies Used

- Python
- Django 6.1.1
- SQLite
- HTML5
- CSS3
- JavaScript
- Chart.js

## Project Structure

```text
personal_expense_tracker/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── local_settings.example.py
│   ├── asgi.py
│   └── wsgi.py
│
├── expenses/
│   ├── migrations/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── templates/
│   ├── expenses/
│   └── registration/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd personal_expense_tracker
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Django secret key

Copy the example settings file:

```bash
cp config/local_settings.example.py config/local_settings.py
```

Generate a new secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Open `config/local_settings.py` and replace the example value with your generated key.

Keep this private file out of GitHub.

### 5. Apply database migrations

```bash
python3 manage.py migrate
```

### 6. Create an administrator account (optional)

```bash
python3 manage.py createsuperuser
```

### 7. Start the development server

```bash
python3 manage.py runserver
```

Open the application:

http://127.0.0.1:8000/

## Application Pages

| Page | URL |
|---|---|
| Registration | `/register/` |
| Login | `/accounts/login/` |
| Dashboard | `/` |
| Add Transaction | `/add/` |
| Monthly Budget | `/budget/` |
| Export CSV | `/export/csv/` |
| Django Admin | `/admin/` |

## Budget Management

Users can set monthly spending limits, monitor expenses, view their remaining budget and receive warnings when spending exceeds the set limit.

## Data Privacy

Transactions and monthly budgets are associated with individual user accounts. Users can only access their own financial records through the application.

## Future Improvements

- Password reset functionality
- Category-wise budget limits
- Downloadable monthly financial reports
- Additional financial analytics
- Production deployment

## Author

Developed as a personal project to practise Python, Django, database management, authentication and web application development.
