# models.py
from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

# --- Filter Models ---

class InstitutionCategory(models.Model):
    """Represents the type of institution (e.g., Private, State, International)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="OTM turi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "OTM Turi"
        verbose_name_plural = "OTM Turlari"

class Location(models.Model):
    """Represents a geographical location (region/city)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Manzil")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Manzil"
        verbose_name_plural = "Manzillar"

class Category(models.Model):
    """Represents the category of an educational direction (e.g., IT, Medicine)."""
    name = models.CharField(max_length=200, unique=True, verbose_name="Ta'lim yo'nalishi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ta'lim Yo'nalishi"
        verbose_name_plural = "Ta'lim Yo'nalishlari"
        ordering = ['name']

class EducationType(models.Model):
    """Represents the type of education (e.g., Full-time, Part-time)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Ta'lim turi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ta'lim Turi"
        verbose_name_plural = "Ta'lim Turlari"

class EducationLanguage(models.Model):
    """Represents the language of instruction."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Ta'lim tili")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ta'lim Tili"
        verbose_name_plural = "Ta'lim Tillari"

class Degree(models.Model):
    """Represents the degree level (e.g., Bachelor, Master)."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Daraja")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Daraja"
        verbose_name_plural = "Darajalar"
 
 
class TuitionFee(models.Model):
    """
    Fee for ONE education‑type inside ONE direction.
    """
    direction = models.ForeignKey(
        'Direction', on_delete=models.CASCADE, related_name="tuition_fees"
    )
    education_type = models.ForeignKey(EducationType, on_delete=models.CASCADE, verbose_name="Ta'lim turi")
    academic_year = models.CharField(max_length=9, blank=True, null=True, verbose_name="O'quv yili")  # e.g. "2024/25"
    local_tuition_fee = models.PositiveIntegerField(blank=True, null=True, verbose_name="Mahalliy kontrakt narxi")
    international_tuition_fee = models.PositiveIntegerField(blank=True, null=True, verbose_name="Xalqaro kontrakt narxi")

    class Meta:
        unique_together = ("direction", "education_type")   # <─ one row per combo
        verbose_name = "Kontrakt narxi"
        verbose_name_plural = "Kontrakt narxlari"
        ordering = ['local_tuition_fee']
        
    def __str__(self):
        return f"{self.direction} · {self.education_type} · {self.local_tuition_fee}"
 
 
class Gallery(models.Model):
    """Represents a gallery of images."""
    university = models.ForeignKey(
        'University',
        on_delete=models.CASCADE,
        related_name="gallery_items"
    )
    image = models.FileField(upload_to='gallery_images/', blank=True, null=True, help_text="Gallery image")
    link = models.URLField(max_length=255, blank=True, null=True, verbose_name="Link")

    def __str__(self):
        return f"Gallery {self.pk}"

# --- Main Models ---

class University(models.Model):
    """Represents a university."""
    full_name = models.CharField(max_length=255, verbose_name="To'liq nomi")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL uchun qisqa nom")
    logo = models.FileField(upload_to='university_logos/', blank=True, null=True, help_text="Logo fayl yo'li") # Assuming path stored as string
    description = RichTextField(blank=True, null=True, verbose_name="Tavsif")
    about_grant = RichTextField(blank=True, null=True, verbose_name="Grant haqida")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manzil")
    has_accomodation = models.BooleanField(default=False, verbose_name="Yotoqxona mavjudmi?")
    has_grant = models.BooleanField(default=False, verbose_name="Grant mavjudmi?")
    admission_phone = models.CharField(max_length=100, blank=True, null=True, verbose_name="Qabul telefoni")
    license_file = models.FileField(upload_to='license_files/', blank=True, null=True, help_text="License file")
    web_site = models.URLField(max_length=255, blank=True, null=True, verbose_name="Veb-sayt")
    instagram_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Instagram")
    telegram_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Telegram")
    facebook_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Facebook")
    youtube_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="YouTube")
    support_email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="Qo'llab-quvvatlash Emaili")
    admission_start_date = models.DateTimeField(blank=True, null=True, verbose_name="Qabul boshlanish sanasi") # Store as Char due to format
    admission_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Qabul tugash sanasi") # Store as Char due to format
    minimal_tuition_fee = models.PositiveIntegerField(blank=True, null=True, verbose_name="Minimal kontrakt narxi")
    maximal_tuition_fee = models.PositiveIntegerField(blank=True, null=True, verbose_name="Maksimal kontrakt narxi")
    latitude = models.CharField(max_length=50, blank=True, null=True, verbose_name="Kenglik")
    longitude = models.CharField(max_length=50, blank=True, null=True, verbose_name="Uzunlik")
    is_open_for_admission = models.BooleanField(default=False, verbose_name="Qabul ochiqmi?")
    
    
    # --- Relationships ---
    institution_category = models.ForeignKey(
        InstitutionCategory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="OTM Turi"
    )
    location = models.ForeignKey( # Assuming one primary location from location key
        Location,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Asosiy Manzil"
    )
    education_types = models.ManyToManyField(
        EducationType,
        blank=True,
        verbose_name="Ta'lim Turlari"
    )
    education_languages = models.ManyToManyField(
        EducationLanguage,
        blank=True,
        verbose_name="Ta'lim Tillari"
    )
    degrees = models.ManyToManyField(
        Degree,
        blank=True,
        verbose_name="Darajalar"
    )
    # gallery = models.JSONField(blank=True, null=True) # Store gallery paths if needed

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
            # Ensure uniqueness if slugifying results in duplicates
            counter = 1
            original_slug = self.slug
            while University.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Universitet"
        verbose_name_plural = "Universitetlar"
        ordering = ['full_name']


class Direction(models.Model):
    """Represents an educational direction within a university."""
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE, # If uni is deleted, delete its directions
        related_name='directions',
        verbose_name="Universitet"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Ta'lim Yo'nalishi Kategoriyasi"
    )
    direction_name = models.CharField(max_length=255, verbose_name="Yo'nalish nomi")
    direction_slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL uchun qisqa nom")
    direction_description = RichTextField(blank=True, null=True, verbose_name="Yo'nalish tavsifi")
    requirement = RichTextField(blank=True, null=True, verbose_name="Talablar")
    first_subject = models.CharField(max_length=100, blank=True, null=True, verbose_name="Birinchi fan")
    second_subject = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ikkinchi fan")
    has_mandatory_subjects = models.BooleanField(default=False, blank=True, null=True, verbose_name="Majburiy fanlar bormi?") # Assuming boolean based on 'true'/'false' string
    has_stipend = models.BooleanField(default=False, verbose_name="Stipendiya mavjudmi?")
    is_open_for_admission = models.BooleanField(default=False, verbose_name="Qabul ochiqmi?")
    application_start_date = models.DateTimeField(blank=True, null=True, verbose_name="Ariza topshirish boshlanish sanasi") # Store as Char due to format
    application_deadline = models.DateTimeField(blank=True, null=True, verbose_name="Ariza topshirish tugash sanasi") # Store as Char due to format
    is_promoted = models.IntegerField(default=0, blank=True, null=True, verbose_name="Targ'ib qilinganmi?") # Assuming integer

    # --- Relationships ---
    education_types = models.ManyToManyField(
        EducationType,
        blank=True,
        verbose_name="Ta'lim Turlari"
    )
    education_languages = models.ManyToManyField(
        EducationLanguage,
        blank=True,
        verbose_name="Ta'lim Tillari"
    )
    degrees = models.ManyToManyField(
        Degree,
        blank=True,
        verbose_name="Darajalar"
    )
    # tuition_fees = models.JSONField(blank=True, null=True) # Store complex tuition fee structure if needed
    # contract_types = models.JSONField(blank=True, null=True) # Store contract types if needed

    def save(self, *args, **kwargs):
        if not self.direction_slug:
            base_slug = slugify(f"{self.university.slug}-{self.direction_name}")
            self.direction_slug = base_slug
            # Ensure uniqueness
            counter = 1
            while Direction.objects.filter(direction_slug=self.direction_slug).exclude(pk=self.pk).exists():
                self.direction_slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.university.full_name} - {self.direction_name}"

    class Meta:
        verbose_name = "Yo'nalish"
        verbose_name_plural = "Yo'nalishlar"
        ordering = ['university__full_name', 'direction_name']

