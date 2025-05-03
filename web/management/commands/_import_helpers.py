# myapp/management/commands/_import_helpers.py
"""
Shared helpers for the university/direction import commands.
Nothing here touches the database schema, so the file can be re‑used by tests.
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote, urljoin
from urllib.request import urlopen

from django.core.files.base import ContentFile
from django.utils.text import slugify

from web.models import (
    Location,
    University,
    Gallery,
)

MENTALABA_CDN = "https://api.mentalaba.uz/"
IMAGE_EXT     = (".jpg", ".jpeg", ".png", ".gif", ".webp")


# ───────────────────────── basic utils ──────────────────────────
def _bool(v) -> bool:
    return v if isinstance(v, bool) else str(v).lower() == "true"


def _url_encode(path: str, cdn: str = MENTALABA_CDN) -> str:
    """Make any incoming URL or relative CDN‑path safe for urlopen()."""
    if not path:
        return ""
    cleaned = path.replace("\xa0", " ").strip().lstrip("/")
    if cleaned.startswith(("http://", "https://")):
        head, tail = cleaned.split("://", 1)
        return f"{head}://{quote(tail, safe='/')}"
    return urljoin(cdn, quote(cleaned, safe="/"))


def _download_file(url: str) -> bytes | None:
    try:
        with urlopen(url) as resp:
            return resp.read()
    except Exception:
        return None


def _attach_remote_file(instance, field_name: str, raw_path: str) -> None:
    """
    Download *raw_path* and save it into **instance.field_name**,
    BUT **only** when the FileField is still empty.
    """
    if not raw_path:
        return

    file_field = getattr(instance, field_name)
    if file_field and file_field.name:          # already has something
        return

    url  = _url_encode(raw_path)
    data = _download_file(url)
    if data:
        filename = os.path.basename(raw_path)
        file_field.save(filename, ContentFile(data), save=False)


# ───────────────────────── model helpers ─────────────────────────
def _get_location(name: str) -> Location | None:
    if not name:
        return None
    try:
        return Location.objects.get(name=name.strip())
    except Location.DoesNotExist:
        return None


def _add_gallery_item(university: University, raw: str) -> None:
    """
    Add **one** gallery entry (image or external link) but never duplicate.
    Called only by the university import routine.
    """
    raw = (raw or "").strip()
    if not raw:
        return

    is_link = raw.startswith(("http://", "https://")) and not raw.lower().endswith(IMAGE_EXT)

    if is_link:
        # simple URL gallery item
        if not university.gallery_items.filter(link=raw).exists():
            Gallery.objects.create(university=university, link=raw)
        return

    # remote image
    filename = os.path.basename(raw)
    if university.gallery_items.filter(image__endswith=filename).exists():
        return

    gal = Gallery.objects.create(university=university)
    _attach_remote_file(gal, "image", raw)
    gal.save()
