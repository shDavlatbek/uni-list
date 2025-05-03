# myapp/management/commands/import_universities.py
from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from web.models import (
    University,
    InstitutionCategory,
    EducationType,
    EducationLanguage,
    Degree,
)

from ._import_helpers import (
    _bool,
    _get_location,
    _attach_remote_file,
    _add_gallery_item,
)

class Command(BaseCommand):
    """
    Import (create or update) universities, including:
    • basic fields
    • logo & licence (only when empty)
    • gallery (added only once)
    • M2M: education_types, education_languages, degrees
    The command is *idempotent* – safe to rerun any time.
    """

    help = "Import universities from a Mentalaba‑format JSON file."

    def add_arguments(self, parser):
        parser.add_argument("universities_json", help="Path to universities.json")

    @transaction.atomic
    def handle(self, *args, **opts):
        u_path = Path(opts["universities_json"]).resolve()
        if not u_path.exists():
            raise CommandError("universities_json file not found")

        universities = json.loads(u_path.read_text(encoding="utf‑8"))

        created = updated = 0

        for u in universities:
            uni_name = u.get("full_name_uz") or u.get("full_name_ru") or u.get("full_name_en")
            uni_slug = u.get("slug") or slugify(uni_name)

            inst_cat = None
            if u.get("institution_category_id"):
                inst_cat = (
                    InstitutionCategory.objects.filter(id=u["institution_category_id"]).first()
                )

            uni_defaults = {
                "id": u.get("id"),
                "full_name": uni_name,
                "slug": uni_slug,
                "description": u.get("description_uz") or "",
                "about_grant": u.get("about_grant_uz") or "",
                "address": u.get("address_uz") or "",
                "founded_year": u.get("founded_year"),
                "students_count": u.get("students_count"),
                "current_quota": u.get("current_quota"),
                "has_accomodation": _bool(u.get("has_accomodation")),
                "has_grant": _bool(u.get("has_grant")),
                "admission_phone": u.get("admission_phone"),
                "web_site": u.get("web_site"),
                "instagram_username": u.get("instagram_username"),
                "telegram_username": u.get("telegram_username"),
                "facebook_username": u.get("facebook_username"),
                "youtube_username": u.get("youtube_username"),
                "support_email": u.get("support_email"),
                "admission_start_date": u.get("admission_start_date"),
                "admission_deadline": u.get("admission_deadline"),
                "minimal_tuition_fee": u.get("minimal_tuition_fee"),
                "maximal_tuition_fee": u.get("maximal_tuition_fee"),
                "latitude": u.get("latitude"),
                "longitude": u.get("longitude"),
                "is_open_for_admission": _bool(u.get("is_open_for_admission")),
                "institution_category": inst_cat,
                "location": _get_location(u.get("location_uz", "")),
            }

            uni, created_flag = University.objects.update_or_create(
                full_name=uni_name,
                defaults=uni_defaults,
            )
            created += int(created_flag)
            updated += int(not created_flag)

            # logo / licence only when blank
            _attach_remote_file(uni, "logo", u.get("logo"))
            lic = (
                u.get("accreditation_certificate")
                or u.get("certification_link")
                or u.get("license_file")
            )
            _attach_remote_file(uni, "license_file", lic)

            # gallery – populate once
            if not uni.gallery_items.exists() and isinstance(u.get("gallery"), list):
                for g_item in u["gallery"]:
                    _add_gallery_item(uni, g_item)

            # m2m sync helpers --------------------------------------------------
            def _resolve_many(model_cls, items, id_key="id", name_keys=None):
                objs = []
                if not isinstance(items, list):
                    return objs
                name_keys = name_keys or ["name_uz", "name_ru", "name_en", "name"]
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
                        objs.append(obj)
                return objs

            if "education_type" in u:
                uni.education_types.set(
                    _resolve_many(EducationType, u["education_type"])
                )
            if "education_language" in u:
                uni.education_languages.set(
                    _resolve_many(EducationLanguage, u["education_language"])
                )
            if "degree" in u:
                uni.degrees.set(_resolve_many(Degree, u["degree"]))

            uni.save()

        self.stdout.write(
            self.style.SUCCESS(f"Universities – created: {created}, updated: {updated}")
        )
 