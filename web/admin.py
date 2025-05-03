from django.contrib import admin
import nested_admin

from web.models import University, Direction, Degree, TuitionFee, Gallery, InstitutionCategory, Location, Category, EducationType, EducationLanguage

class TuitionFeeInline(nested_admin.NestedStackedInline):
    extra = 0
    model = TuitionFee

class DirectionInline(nested_admin.NestedStackedInline):
    extra = 0
    model = Direction
    inlines = [TuitionFeeInline]


class DirectionAdmin(nested_admin.NestedModelAdmin):
    extra = 0
    inlines = [TuitionFeeInline]


class GalleryInline(nested_admin.NestedStackedInline):
    extra = 0
    model = Gallery


class UniversityAdmin(nested_admin.NestedModelAdmin):
    extra = 0
    inlines = [DirectionInline, GalleryInline]
    

# Register your models here.
admin.site.register(University, UniversityAdmin)
admin.site.register(Direction, DirectionAdmin)
admin.site.register(InstitutionCategory)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(EducationType)
admin.site.register(EducationLanguage)
admin.site.register(Degree)

