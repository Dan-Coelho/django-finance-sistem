from django.urls import path

from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='list'),  # List all transactions
    path('create/income/', views.CreateIncomeView.as_view(), name='create-income'),  # Create income transaction
    path('create/expense/', views.CreateExpenseView.as_view(), name='create-expense'),  # Create expense transaction
    path('<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='edit'),  # Edit transaction
    path('<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='delete'),  # Delete transaction
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='detail'),  # View transaction detail
    path('export/csv/', views.export_transactions_csv, name='export-csv'),  # Export transactions to CSV
    path('export/pdf/', views.export_report_pdf, name='export-pdf'),  # Export report to PDF
]
