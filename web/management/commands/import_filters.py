# <your_app>/management/commands/import_filters.py
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from web.models import (  # adjust the import path to your project
    InstitutionCategory,
    Location,
    Category,
    EducationType,
    EducationLanguage,
)

# -- Helpers ---------------------------------------------------------------

MODEL_MAP = {
    "institution_category_id": InstitutionCategory,
    "location": Location,
    "category": Category,
    "edu_type": EducationType,
    "edu_lang": EducationLanguage,
}


def _upsert_objects(model, records):
    """
    Create new rows or update the name if the id already exists.
    Uses bulk operations for speed.
    """
    objs = []
    ids_seen = set()

    # First pull already-existing rows so we can decide what needs updating
    existing = {obj.pk: obj for obj in model.objects.filter(pk__in=[r["id"] for r in records])}

    for rec in records:
        pk = int(rec["id"])
        name = rec["name"].strip()
        ids_seen.add(pk)

        if pk in existing:
            # Only update if the name changed
            obj = existing[pk]
            if obj.name != name:
                obj.name = name
                obj.save(update_fields=["name"])
        else:
            objs.append(model(id=pk, name=name))

    if objs:
        model.objects.bulk_create(objs, ignore_conflicts=True)

    # Optionally: deactivate / delete rows no longer present
    # model.objects.exclude(pk__in=ids_seen).delete()


# -- Management command ----------------------------------------------------

class Command(BaseCommand):
    """
    Example:
        python manage.py import_filters data/filters.json
    """

    help = "Import filter lookup values (institution categories, locations, ...) "\
           "from a JSON definition produced by the front-end."

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to the filters.json file")

    @transaction.atomic
    def handle(self, *args, **options):
        json_path = Path(options["json_file"]).expanduser().resolve()

        if not json_path.exists():
            raise CommandError(f"File not found: {json_path}")

        try:
            with json_path.open(encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(f"Could not read JSON – {exc}")

        created, updated, skipped = 0, 0, 0

        for item in data:
            name_key = item.get("name")
            model = MODEL_MAP.get(name_key)

            # Only process filters that map to one of our lookup tables
            if model and isinstance(item.get("value"), list):
                _upsert_objects(model, item["value"])
                self.stdout.write(self.style.SUCCESS(f"✔  Synced {model.__name__}"))
                created += 1
            else:
                skipped += 1

        self.stdout.write("")  # blank line
        self.stdout.write(self.style.SUCCESS(f"Completed. "
                                             f"Processed: {created}, Skipped: {skipped}"))
