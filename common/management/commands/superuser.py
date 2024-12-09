from typing import Any
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from common.management.data_fixtures import superusers
from people.models import CustomUser


class Command(BaseCommand):
    help = "Create superuser"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Creating superuser")
        self._cerate_super_users(superusers=superusers)

    def _cerate_super_users(self, superusers):
        for superuser_dict in superusers:
            try:
                superuser_obj = CustomUser.objects.create_superuser(**superuser_dict)
                self.stdout.write(f"Created superuser {superuser_obj.email} as {superuser_dict['role']}")
            except IntegrityError:
                self.stderr.write(f"Superuser {superuser_dict['email']} already exists")
