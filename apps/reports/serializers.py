from rest_framework import serializers
from .models import (
    Warehouse, DailyReport, PaymentEntry, InstallmentItem, 
    Expense, Debt, DebtRepayment, ExpenseCategory
)
from django.db import transaction

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'

class PaymentEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentEntry
        fields = ['payment_type', 'amount']

class InstallmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentItem
        fields = ['provider', 'months', 'amount', 'commission']

class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'comment', 'employee_name']

class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ['client_name', 'phone_number', 'amount', 'date']

class DebtRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtRepayment
        fields = ['client_name', 'amount', 'date']

class DailyReportSerializer(serializers.ModelSerializer):
    payments = PaymentEntrySerializer(many=True)
    installments = InstallmentItemSerializer(many=True)
    expenses = ExpenseSerializer(many=True)
    debts = DebtSerializer(many=True)
    debt_repayments = DebtRepaymentSerializer(many=True)
    warehouse_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = DailyReport
        fields = [
            'id', 'date', 'warehouse_id', 'gross_sales', 'returns_amount', 
            'submitted_cash', 'payments', 'installments', 'expenses', 
            'debts', 'debt_repayments', 'created_at', 'updated_at'
        ]

    @transaction.atomic
    def create(self, validated_data):
        payments_data = validated_data.pop('payments', [])
        installments_data = validated_data.pop('installments', [])
        expenses_data = validated_data.pop('expenses', [])
        debts_data = validated_data.pop('debts', [])
        repayments_data = validated_data.pop('debt_repayments', [])
        
        warehouse_id = validated_data.pop('warehouse_id')
        date = validated_data.get('date')

        # Sync logic: Update if exists, else create
        report, created = DailyReport.objects.update_or_create(
            date=date,
            warehouse_id=warehouse_id,
            defaults=validated_data
        )

        # Clear existing related data for update
        report.payments.all().delete()
        report.installments.all().delete()
        report.expenses.all().delete()
        report.debts.all().delete()
        report.debt_repayments.all().delete()

        # Create new related data
        for data in payments_data:
            PaymentEntry.objects.create(report=report, **data)
        for data in installments_data:
            InstallmentItem.objects.create(report=report, **data)
        for data in expenses_data:
            Expense.objects.create(report=report, **data)
        for data in debts_data:
            Debt.objects.create(report=report, **data)
        for data in repayments_data:
            DebtRepayment.objects.create(report=report, **data)

        return report
