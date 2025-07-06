from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
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


def fetch_data_view(request):
    """Custom admin view for fetching data"""
    if request.method == 'POST' and 'fetch_data' in request.POST:
        # This is where we'll add the fetch data logic later
        messages.success(request, 'Data fetch initiated successfully!')
        return HttpResponseRedirect(request.get_full_path())
    
    context = {
        'title': 'Fetch Data',
        'site_title': admin.site.site_title,
        'site_header': admin.site.site_header,
        'has_permission': request.user.is_staff,
    }
    
    return TemplateResponse(request, 'admin/fetch_data.html', context)


# Custom AdminSite to add our custom view
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-data/', self.admin_view(fetch_data_view), name='fetch_data'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)
        
        # Add our custom fetch data section
        fetch_data_app = {
            'name': 'Data Management',
            'app_label': 'data_management',
            'app_url': '',
            'has_module_perms': True,
            'models': [{
                'name': 'Fetch Data',
                'object_name': 'FetchData',
                'admin_url': '/admin/fetch-data/',
                'add_url': None,
                'view_only': True,
            }]
        }
        
        app_list.append(fetch_data_app)
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
            'app_list': app_list,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/index.html', context)


# Use our custom admin site instead of the default one
admin_site = CustomAdminSite(name='admin')


# Register your models here.
admin_site.register(University, UniversityAdmin)
admin_site.register(Direction, DirectionAdmin)
admin_site.register(InstitutionCategory)
admin_site.register(Location)
admin_site.register(Category)
admin_site.register(EducationType)
admin_site.register(EducationLanguage)
admin_site.register(Degree)

# Also register with default admin site for backward compatibility
admin.site.register(University, UniversityAdmin)
admin.site.register(Direction, DirectionAdmin)
admin.site.register(InstitutionCategory)
admin.site.register(Location)
admin.site.register(Category)
admin.site.register(EducationType)
admin.site.register(EducationLanguage)
admin.site.register(Degree)

