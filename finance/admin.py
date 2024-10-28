from django.contrib import admin

from finance.models import FinancialAccount, Loan, Repayment, Transaction

admin.site.register(FinancialAccount)
admin.site.register(Loan)
admin.site.register(Repayment)
admin.site.register(Transaction)
