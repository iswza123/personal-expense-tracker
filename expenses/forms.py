
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, MonthlyBudget


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction

        fields = [
            'title',
            'amount',
            'transaction_type',
            'category',
            'date',
            'description',
        ]

        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 3}
            ),
        }



class MonthlyBudgetForm(forms.ModelForm):

    amount_limit = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={'step': '0.01', 'placeholder': 'Enter monthly budget'}
        )
    )

    class Meta:
        model = MonthlyBudget

        fields = [
            'month',
            'year',
            'amount_limit',
        ]

        widgets = {
            'year': forms.NumberInput(
                attrs={'min': 2000, 'max': 2100}
            ),
        }


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
