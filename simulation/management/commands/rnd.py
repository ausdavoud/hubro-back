from typing import Any

from django.core.management.base import BaseCommand

from ...models.simulation import RnDStatic
from ..static_objects import RnD_statics


class Command(BaseCommand):
    help = "Populates predefined R&D static items in database"

    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write(f"Adding {len(RnD_statics)} R&D static items to database.")

        for index, rnd_static_dict in enumerate(RnD_statics):
            try:
                rnd_static_obj, created = RnDStatic.objects.get_or_create(**rnd_static_dict)
            except RnDStatic.MultipleObjectsReturned:
                self.stderr.write(f"{index + 1:2}. Found multiple records with title: {rnd_static_dict['title']}")
                continue
            if created:
                self.stdout.write(f"{index + 1:2}. Added record with title: {rnd_static_obj.title}")
                continue
            self.stderr.write(f"{index + 1:2}. Found record with title: {rnd_static_obj.title}")
