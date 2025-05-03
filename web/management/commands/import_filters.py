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
    Degree
)

# -- Helpers ---------------------------------------------------------------

MODEL_MAP = {
    "institution_category_id": InstitutionCategory,
    "location": Location,
    "category": Category,
    "edu_type": EducationType,
    "edu_lang": EducationLanguage,
    "degree": Degree
}


def _upsert_objects(model, records):
    """
    Create new rows or update existing ones, preserving IDs from the filters.json file.
    """
    for rec in records:
        name = rec["name"].strip()
        id_value = rec.get("id")
        
        if id_value:
            # Try to find by ID first
            try:
                obj = model.objects.filter(id=id_value).first()
                if obj:
                    # If object exists with this ID, update its name
                    if obj.name != name:
                        obj.name = name
                        obj.save()
                else:
                    # Create new object with specified ID
                    obj = model.objects.create(id=id_value, name=name)
            except Exception as e:
                print(f"Error processing {name} with ID {id_value}: {e}")
        else:
            # Fallback to get_or_create by name if no ID provided
            obj, created = model.objects.get_or_create(name=name)


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
