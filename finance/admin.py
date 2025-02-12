from django.contrib import admin

from finance.models import (
    CashChange,
    FinancialAccount,
    Loan,
    Overdraft,
    Repayment,
    Transaction,
)


class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "type"]


class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "team",
        "category",
        "quarter",
        "financial_account",
        "debit_amount",
        "credit_amount",
    ]


class OverdraftAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "team",
        "quarter",
        "beginning_overdraft",
        "ending_overdraft",
    ]


class CashChangeAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "quarter", "beginning_cash", "ending_cash"]


class LoanAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "team",
        "issued_quarter",
        "amount",
        "payback_period",
        "total_payback",
        "payback_per_quarter",
    ]


class RepaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "team", "repayment_amount", "quarter", "loan"]


admin.site.register(FinancialAccount, FinancialAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Overdraft, OverdraftAdmin)
admin.site.register(CashChange, CashChangeAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Repayment, RepaymentAdmin)
