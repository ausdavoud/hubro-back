from typing import Any

from django.core.management.base import BaseCommand

from ...models.rd import StaticRD
from ..data_fixtures import static_rd


class Command(BaseCommand):
    help = "Populates predefined R&D static items in database"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write(f"Adding {len(static_rd)} R&D static items to database.")

        for index, rnd_static_dict in enumerate(static_rd):
            try:
                rnd_static_obj, created = StaticRD.objects.get_or_create(**rnd_static_dict)
            except StaticRD.MultipleObjectsReturned:
                self.stderr.write(f"{index + 1:2}. Found multiple records with title: {rnd_static_dict['title']}")
                continue
            if created:
                self.stdout.write(f"{index + 1:2}. Added record with title: {rnd_static_obj.title}")
                continue
            self.stderr.write(f"{index + 1:2}. Found previously added record with title: {rnd_static_obj.title}")
