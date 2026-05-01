from django.db import models
from django.contrib.auth.models import User

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class DailyReport(models.Model):
    date = models.DateField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='reports')
    gross_sales = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    returns_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    submitted_cash = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('date', 'warehouse')

    def __str__(self):
        return f"{self.date} - {self.warehouse.name}"

class PaymentEntry(models.Model):
    PAYMENT_CHOICES = (
        ('Uzcard', 'Uzcard'),
        ('Humo', 'Humo'),
        ('Click', 'Click'),
        ('TransferClick', 'TransferClick'),
    )
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

class InstallmentItem(models.Model):
    PROVIDER_CHOICES = (
        ('Uzum', 'Uzum'),
        ('Alif', 'Alif'),
    )
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='installments')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    months = models.IntegerField()
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    commission = models.DecimalField(max_digits=20, decimal_places=2)

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Expense(models.Model):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='expenses')
    category = models.CharField(max_length=255) # Keep CharField as per TZ, but maybe link to ExpenseCategory later
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    comment = models.TextField()
    employee_name = models.CharField(max_length=255, blank=True, null=True)

class Debt(models.Model):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='debts')
    client_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()

class DebtRepayment(models.Model):
    report = models.ForeignKey(DailyReport, on_delete=models.CASCADE, related_name='debt_repayments')
    client_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
