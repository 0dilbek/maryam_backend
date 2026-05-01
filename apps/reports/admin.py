from django.contrib import admin
from .models import (
    Warehouse, DailyReport, PaymentEntry, InstallmentItem, 
    Expense, Debt, DebtRepayment, ExpenseCategory
)

class PaymentEntryInline(admin.TabularInline):
    model = PaymentEntry
    extra = 0

class InstallmentItemInline(admin.TabularInline):
    model = InstallmentItem
    extra = 0

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0

class DebtInline(admin.TabularInline):
    model = Debt
    extra = 0

class DebtRepaymentInline(admin.TabularInline):
    model = DebtRepayment
    extra = 0

@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'warehouse', 'gross_sales', 'submitted_cash')
    list_filter = ('date', 'warehouse')
    inlines = [
        PaymentEntryInline, InstallmentItemInline, 
        ExpenseInline, DebtInline, DebtRepaymentInline
    ]

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
