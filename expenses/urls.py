from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('budget/', views.manage_budget, name='manage_budget'),
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('edit/<int:id>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:id>/', views.delete_transaction, name='delete_transaction'),
    path('export/csv/', views.export_transactions_csv, name='export_transactions_csv'),
]