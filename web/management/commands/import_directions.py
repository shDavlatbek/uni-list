# myapp/management/commands/import_directions.py
from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from web.models import (
    University,
    Direction,
    Category,
    EducationType,
    EducationLanguage,
    Degree,
    TuitionFee,
)

from ._import_helpers import _bool

class Command(BaseCommand):
    """Create / update directions using *university_id* straight from JSON."""

    help = "Import directions (plus tuition‑fees) from Mentalaba‑style JSON."

    def add_arguments(self, parser):
        parser.add_argument("directions_json", help="Path to directions.json")

    @transaction.atomic
    def handle(self, *args, **opts):
        d_path = Path(opts["directions_json"]).resolve()
        if not d_path.exists():
            raise CommandError("directions_json not found")

        directions = json.loads(d_path.read_text(encoding="utf‑8"))

        created = updated = skipped = 0

        for d in directions:
            uni_id = d.get("university_id")
            if not uni_id:
                skipped += 1
                continue

            try:
                uni = University.objects.get(id=uni_id)
            except University.DoesNotExist:
                # University not in DB yet → skip for now
                print(f"University {uni_id} {d} not found")
                skipped += 1
                continue

            dir_name = d.get("direction_name_uz") or d.get("direction_name_ru") or "Unnamed"
            dir_slug = d.get("direction_slug") or slugify(f"{uni.slug}-{dir_name}")

            category = None
            if d.get("category_id"):
                category = Category.objects.filter(id=d["category_id"]).first()

            dir_defaults = {
                "direction_name": dir_name,
                "direction_slug": dir_slug,
                "direction_description": d.get("direction_description_uz") or "",
                "requirement": d.get("requirement_uz") or "",
                "first_subject": d.get("first_subject"),
                "second_subject": d.get("second_subject"),
                "has_mandatory_subjects": _bool(d.get("has_mandatory_subjects")),
                "has_stipend": _bool(d.get("has_stipend")),
                "is_open_for_admission": _bool(d.get("is_open_for_admission")),
                "application_start_date": d.get("application_start_date"),
                "application_deadline": d.get("application_deadline"),
                "status": d.get("status") or "active",
                "is_promoted": d.get("is_promoted") or 0,
                "category": category,
            }

            dir_obj, created_flag = Direction.objects.update_or_create(
                direction_name=dir_name,
                university=uni,
                defaults=dir_defaults,
            )
            created += int(created_flag)
            updated += int(not created_flag)

            # ─────────── Many‑to‑many helpers ───────────
            def _resolve_many(model_cls, items, id_key, *name_keys):
                found = []
                if not isinstance(items, list):
                    return found
                for itm in items:
                    obj = None
                    for nk in name_keys:
                        if itm.get(nk):
                            obj = model_cls.objects.filter(name=itm[nk]).first()
                            if obj:
                                break
                    if not obj and itm.get(id_key):
                        obj = model_cls.objects.filter(id=itm[id_key]).first()
                    if obj:
                        found.append(obj)
                return found

            dir_obj.education_types.set(
                _resolve_many(
                    EducationType,
                    d.get("education_types", []),
                    "education_type_id",
                    "education_type_name_uz", "education_type_name_ru", "education_type_name_en",
                )
            )
            dir_obj.education_languages.set(
                _resolve_many(
                    EducationLanguage,
                    d.get("education_languages", []),
                    "education_language_id",
                    "education_language_name_uz", "education_language_name_ru", "education_language_name_en",
                )
            )
            dir_obj.degrees.set(
                _resolve_many(
                    Degree,
                    d.get("degrees", []),
                    "degree_id",
                    "degree_name_uz", "degree_name_ru", "degree_name_en",
                )
            )

            # tuition fees
            for fee in d.get("tuition_fees", []):
                et = None
                et_name = (
                    fee.get("education_type_name_uz")
                    or fee.get("education_type_name_ru")
                    or fee.get("education_type_name_en")
                )
                if et_name:
                    et = EducationType.objects.filter(name=et_name).first()
                if not et and fee.get("education_type_id"):
                    et = EducationType.objects.filter(id=fee["education_type_id"]).first()
                if not et:
                    continue

                TuitionFee.objects.update_or_create(
                    direction=dir_obj,
                    education_type=et,
                    defaults={
                        "academic_year": fee.get("academic_year"),
                        "local_tuition_fee": fee.get("local_tuition_fee"),
                        "international_tuition_fee": fee.get("international_tuition_fee"),
                    },
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Directions – created: {created}, updated: {updated}, skipped (missing university): {skipped}"))
