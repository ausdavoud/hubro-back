from django.contrib import admin

from finance.models import CashChange, FinancialAccount, Loan, Overdraft, Repayment, Transaction


class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "type"]


class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "category",
        "quarter",
        "financial_account",
        "debit_amount",
        "credit_amount",
    ]


class OverdraftAdmin(admin.ModelAdmin):
    list_display = ["id", "player", "quarter", "beginning_overdraft", "ending_overdraft"]


class CashChangeAdmin(admin.ModelAdmin):
    list_display = ["id", "player", "quarter", "beginning_cash", "ending_cash"]


class LoanAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "issued_quarter",
        "amount",
        "payback_period",
        "total_payback",
        "payback_per_quarter",
    ]


class RepaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "player", "repayment_amount", "quarter", "loan"]


admin.site.register(FinancialAccount, FinancialAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Overdraft, OverdraftAdmin)
admin.site.register(CashChange, CashChangeAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Repayment, RepaymentAdmin)
