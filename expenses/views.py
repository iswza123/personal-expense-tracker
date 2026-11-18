import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import Transaction, MonthlyBudget
from .forms import TransactionForm, MonthlyBudgetForm, RegistrationForm


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()

    return render(
        request,
        'expenses/add_transaction.html',
        {'form': form}
    )


@login_required
def edit_transaction(request, id):
    transaction = get_object_or_404(
        Transaction,
        id=id,
        user=request.user
    )

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)

        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(instance=transaction)

    return render(
        request,
        'expenses/edit_transaction.html',
        {'form': form}
    )


@login_required
def delete_transaction(request, id):
    transaction = get_object_or_404(
        Transaction,
        id=id,
        user=request.user
    )

    if request.method == 'POST':
        transaction.delete()
        return redirect('dashboard')

    return render(
        request,
        'expenses/delete_transaction.html',
        {'transaction': transaction}
    )


@login_required
def dashboard(request):

    # All user transactions
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    # Overall income and expenses
    total_income = transactions.filter(
        transaction_type='Income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = transactions.filter(
        transaction_type='Expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = total_income - total_expenses

    # Monthly report
    selected_month = request.GET.get('month', '')

    monthly_transactions = Transaction.objects.filter(
        user=request.user
    )

    if selected_month:
        try:
            year, month = map(int, selected_month.split('-'))

            if 1 <= month <= 12:
                monthly_transactions = monthly_transactions.filter(
                    date__year=year,
                    date__month=month
                )
            else:
                selected_month = ''
        except (ValueError, TypeError):
            selected_month = ''

    monthly_income = monthly_transactions.filter(
        transaction_type='Income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    monthly_expenses = monthly_transactions.filter(
        transaction_type='Expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    monthly_balance = monthly_income - monthly_expenses

    # Monthly chart data
    monthly_data = (
        Transaction.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(
            income=Sum(
                'amount',
                filter=Q(transaction_type='Income')
            ),
            expenses=Sum(
                'amount',
                filter=Q(transaction_type='Expense')
            )
        )
        .order_by('month')
    )

    chart_months = [
        item['month'].strftime('%b %Y')
        for item in monthly_data
    ]

    chart_income = [
        float(item['income'] or 0)
        for item in monthly_data
    ]

    chart_expenses = [
        float(item['expenses'] or 0)
        for item in monthly_data
    ]

    # Category-wise expense chart data
    category_data = (
        Transaction.objects.filter(
            user=request.user,
            transaction_type='Expense'
        )
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('category')
    )

    category_labels = [
        item['category']
        for item in category_data
    ]

    category_amounts = [
        float(item['total'])
        for item in category_data
    ]

    # Search filter
    search_query = request.GET.get('q', '')

    if search_query:
        transactions = transactions.filter(
            title__icontains=search_query
        )

    # Transaction type filter
    transaction_type = request.GET.get('type', '')

    if transaction_type in ['Income', 'Expense']:
        transactions = transactions.filter(
            transaction_type=transaction_type
        )
    else:
        transaction_type = ''

    # Category filter
    category = request.GET.get('category', '')

    valid_categories = [
        'Food',
        'Travel',
        'Shopping',
        'Bills',
        'Salary',
        'Other'
    ]

    if category in valid_categories:
        transactions = transactions.filter(
            category=category
        )
    else:
        category = ''

    # Date range filter
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    if start_date:
        transactions = transactions.filter(
            date__gte=start_date
        )

    if end_date:
        transactions = transactions.filter(
            date__lte=end_date
        )


    # Monthly budget calculations
    today = timezone.localdate()

    budget_year = today.year
    budget_month = today.month

    if selected_month:
        try:
            selected_year, selected_month_number = map(
                int, selected_month.split('-')
            )
            if 1 <= selected_month_number <= 12:
                budget_year = selected_year
                budget_month = selected_month_number
        except (ValueError, TypeError):
            pass

    monthly_budget = MonthlyBudget.objects.filter(
        user=request.user,
        year=budget_year,
        month=budget_month
    ).first()

    budget_spent = Transaction.objects.filter(
        user=request.user,
        transaction_type='Expense',
        date__year=budget_year,
        date__month=budget_month
    ).aggregate(total=Sum('amount'))['total'] or 0

    if monthly_budget:
        budget_limit = monthly_budget.amount_limit
        budget_remaining = max(budget_limit - budget_spent, 0)
        budget_over_amount = max(budget_spent - budget_limit, 0)

        budget_percentage = (
            float(budget_spent / budget_limit * 100)
            if budget_limit > 0 else 0
        )
        budget_progress = min(budget_percentage, 100)
    else:
        budget_limit = 0
        budget_remaining = 0
        budget_over_amount = 0
        budget_percentage = 0
        budget_progress = 0

    budget_month_label = (
        f"{dict(MonthlyBudget.MONTH_CHOICES).get(budget_month)} "
        f"{budget_year}"
    )

    # Dashboard context
    context = {
        'transactions': transactions,

        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,

        'chart_months': chart_months,
        'chart_income': chart_income,
        'chart_expenses': chart_expenses,

        'category_labels': category_labels,
        'category_amounts': category_amounts,

        'search_query': search_query,
        'transaction_type': transaction_type,
        'category': category,

        'start_date': start_date,
        'end_date': end_date,

        'selected_month': selected_month,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_balance': monthly_balance,

        'monthly_budget': monthly_budget,
        'budget_month_label': budget_month_label,
        'budget_limit': budget_limit,
        'budget_spent': budget_spent,
        'budget_remaining': budget_remaining,
        'budget_over_amount': budget_over_amount,
        'budget_percentage': budget_percentage,
        'budget_progress': budget_progress,
    }

    return render(
        request,
        'expenses/dashboard.html',
        context
    )


@login_required
def export_transactions_csv(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date', '-id')

    response = HttpResponse(
        content_type='text/csv; charset=utf-8'
    )
    response['Content-Disposition'] = (
        'attachment; filename="personal_expense_transactions.csv"'
    )

    response.write('\ufeff')

    writer = csv.writer(response)

    writer.writerow([
        'Date',
        'Title',
        'Transaction Type',
        'Category',
        'Amount',
        'Description'
    ])

    for transaction in transactions:
        writer.writerow([
            transaction.date,
            transaction.title,
            transaction.transaction_type,
            transaction.category,
            transaction.amount,
            transaction.description
        ])

    return response



@login_required
def manage_budget(request):
    today = timezone.localdate()

    if request.method == 'POST':
        form = MonthlyBudgetForm(request.POST)

        if form.is_valid():
            MonthlyBudget.objects.update_or_create(
                user=request.user,
                year=form.cleaned_data['year'],
                month=form.cleaned_data['month'],
                defaults={
                    'amount_limit': form.cleaned_data['amount_limit']
                }
            )

            return redirect('dashboard')

    else:
        current_budget = MonthlyBudget.objects.filter(
            user=request.user,
            year=today.year,
            month=today.month
        ).first()

        if current_budget:
            form = MonthlyBudgetForm(instance=current_budget)
        else:
            form = MonthlyBudgetForm(
                initial={
                    'month': today.month,
                    'year': today.year
                }
            )

    return render(
        request,
        'expenses/manage_budget.html',
        {'form': form}
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )
