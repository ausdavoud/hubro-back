from typing import Any
from django.core.management.base import BaseCommand, CommandError

from ...models.simulation import RnDStatic

from ...constants.static_objects import RnD_static_objects

class Command(BaseCommand):
    help = 'Populates predefined R&D static objects'

    def handle(self, *args: Any, **options: Any) -> str | None:
        for rnd_static_object in RnD_static_objects:
            rnd_static = RnDStatic(**rnd_static_object)
            rnd_static.save()
            self.stdout.write(f'Add R&D database record. Title: {rnd_static.title}')