# models.py
from django.db import models
from django.utils.text import slugify

# --- Filter Models ---

class InstitutionCategory(models.Model):
    """Represents the type of institution (e.g., Private, State, International)."""
    id = models.PositiveIntegerField(primary_key=True, help_text="ID from filters.json")
    name = models.CharField(max_length=100, unique=True, verbose_name="OTM turi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "OTM Turi"
        verbose_name_plural = "OTM Turlari"

class Location(models.Model):
    """Represents a geographical location (region/city)."""
    id = models.PositiveIntegerField(primary_key=True, help_text="ID from filters.json")
    name = models.CharField(max_length=100, unique=True, verbose_name="Manzil")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Manzil"
        verbose_name_plural = "Manzillar"

class Category(models.Model):
    """Represents the category of an educational direction (e.g., IT, Medicine)."""
    id = models.PositiveIntegerField(primary_key=True, help_text="ID from filters.json")
    name = models.CharField(max_length=200, unique=True, verbose_name="Ta'lim yo'nalishi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ta'lim Yo'nalishi"
        verbose_name_plural = "Ta'lim Yo'nalishlari"
        ordering = ['name']

class EducationType(models.Model):
    """Represents the type of education (e.g., Full-time, Part-time)."""
    id = models.PositiveIntegerField(primary_key=True, help_text="ID from filters.json")
    name = models.CharField(max_length=100, unique=True, verbose_name="Ta'lim turi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ta'lim Turi"
        verbose_name_plural = "Ta'lim Turlari"

class EducationLanguage(models.Model):
    """Represents the language of instruction."""
    id = models.PositiveIntegerField(primary_key=True, help_text="ID from filters.json")
    name = models.CharField(max_length=100, unique=True, verbose_name="Ta'lim tili")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ta'lim Tili"
        verbose_name_plural = "Ta'lim Tillari"

class Degree(models.Model):
    """Represents the degree level (e.g., Bachelor, Master)."""
    # Assuming degree IDs are consistent across universities in the JSON
    id = models.PositiveIntegerField(primary_key=True)
    # We need a name field, inferring from direction-keys sample
    name = models.CharField(max_length=100, unique=True, default="Noma'lum Daraja", verbose_name="Daraja")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Daraja"
        verbose_name_plural = "Darajalar"

# --- Main Models ---

class University(models.Model):
    """Represents a university."""
    id = models.PositiveIntegerField(primary_key=True, help_text="Original ID from JSON")
    full_name = models.CharField(max_length=255, verbose_name="To'liq nomi")
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="URL uchun qisqa nom")
    logo = models.CharField(max_length=255, blank=True, null=True, help_text="Logo fayl yo'li") # Assuming path stored as string
    description = models.TextField(blank=True, null=True, verbose_name="Tavsif")
    about_grant = models.TextField(blank=True, null=True, verbose_name="Grant haqida")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Manzil")
    founded_year = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tashkil etilgan yili") # Store as Char due to format
    students_count = models.PositiveIntegerField(blank=True, null=True, verbose_name="Talabalar soni")
    current_quota = models.PositiveIntegerField(blank=True, null=True, verbose_name="Joriy kvota")
    has_accomodation = models.BooleanField(default=False, verbose_name="Yotoqxona mavjudmi?")
    has_grant = models.BooleanField(default=False, blank=True, null=True, verbose_name="Grant mavjudmi?")
    admission_phone = models.CharField(max_length=100, blank=True, null=True, verbose_name="Qabul telefoni")
    web_site = models.URLField(max_length=255, blank=True, null=True, verbose_name="Veb-sayt")
    instagram_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Instagram")
    telegram_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Telegram")
    facebook_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="Facebook")
    youtube_username = models.CharField(max_length=255, blank=True, null=True, verbose_name="YouTube")
    support_email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="Qo'llab-quvvatlash Emaili")
    admission_start_date = models.CharField(max_length=50, blank=True, null=True, verbose_name="Qabul boshlanish sanasi") # Store as Char due to format
    admission_deadline = models.CharField(max_length=50, blank=True, null=True, verbose_name="Qabul tugash sanasi") # Store as Char due to format
    minimal_tuition_fee = models.PositiveIntegerField(blank=True, null=True, verbose_name="Minimal kontrakt narxi")
    maximal_tuition_fee = models.PositiveIntegerField(blank=True, null=True, verbose_name="Maksimal kontrakt narxi")
    latitude = models.CharField(max_length=50, blank=True, null=True, verbose_name="Kenglik")
    longitude = models.CharField(max_length=50, blank=True, null=True, verbose_name="Uzunlik")
    is_open_for_admission = models.BooleanField(default=False, verbose_name="Qabul ochiqmi?")
    rating = models.CharField(max_length=10, blank=True, null=True, verbose_name="Reyting")
    rating_total_pupil = models.PositiveIntegerField(blank=True, null=True, verbose_name="Reytingdagi o'quvchilar soni")
    mtdt_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Meta Sarlavha")
    mtdt_description = models.TextField(blank=True, null=True, verbose_name="Meta Tavsif")
    direction_count = models.PositiveIntegerField(blank=True, null=True, verbose_name="Yo'nalishlar soni")

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
    direction_id = models.PositiveIntegerField(primary_key=True, help_text="Original direction_id from JSON")
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
    direction_description = models.TextField(blank=True, null=True, verbose_name="Yo'nalish tavsifi")
    requirement = models.TextField(blank=True, null=True, verbose_name="Talablar")
    first_subject = models.CharField(max_length=100, blank=True, null=True, verbose_name="Birinchi fan")
    second_subject = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ikkinchi fan")
    has_mandatory_subjects = models.BooleanField(default=False, blank=True, null=True, verbose_name="Majburiy fanlar bormi?") # Assuming boolean based on 'true'/'false' string
    has_stipend = models.BooleanField(default=False, verbose_name="Stipendiya mavjudmi?")
    is_open_for_admission = models.BooleanField(default=False, verbose_name="Qabul ochiqmi?")
    application_start_date = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ariza topshirish boshlanish sanasi") # Store as Char due to format
    application_deadline = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ariza topshirish tugash sanasi") # Store as Char due to format
    status = models.CharField(max_length=50, blank=True, null=True, default='active', verbose_name="Holati")
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

