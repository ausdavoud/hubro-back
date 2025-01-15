from typing import Any

from django.core.management.base import BaseCommand

from common.management.data_fixtures import FINANCIAL_ACCOUNTS
from finance.models import FinancialAccount


class Command(BaseCommand):
    help = "Populates predefined Financial Accounts in database"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write(f"Adding {len(FINANCIAL_ACCOUNTS)} financial accounts to database.")

        for index, financial_account_dict in enumerate(FINANCIAL_ACCOUNTS):
            try:
                financial_account_obj, created = FinancialAccount.objects.get_or_create(**financial_account_dict)
            except FinancialAccount.MultipleObjectsReturned:
                self.stderr.write(f"{index + 1:2}. Found multiple records with name: {financial_account_dict['name']}")
                continue
            if created:
                self.stdout.write(f"{index + 1:2}. Added record with name: {financial_account_obj.code}")
                continue
            self.stderr.write(f"{index + 1:2}. Found record with name: {financial_account_obj.code}")
