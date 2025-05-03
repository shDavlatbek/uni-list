from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.urls import reverse

from .models import (
    University, Direction, 
    InstitutionCategory, Location, Category, 
    EducationType, EducationLanguage, Degree
)

def home_view(request):
    """Home page view that displays featured universities."""
    # Get 6 universities that are open for admission
    featured_universities = University.objects.filter(
        is_open_for_admission=True
    )[:6]  # Mix of promoted and random
    
    # Counts for stats section
    university_count = University.objects.count()
    direction_count = Direction.objects.count()
    location_count = Location.objects.count()
    
    context = {
        'featured_universities': featured_universities,
        'university_count': university_count,
        'direction_count': direction_count,
        'location_count': location_count,
    }
    
    return render(request, 'universities/home.html', context)


class UniversityListView(ListView):
    """View for listing universities with filters."""
    model = University
    template_name = 'universities/university_list.html'
    context_object_name = 'universities'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = University.objects.all()
        
        # Apply filters if present in GET parameters
        # Filter by institution category - support for multiple values
        institution_categories = self.request.GET.getlist('institution_category')
        if institution_categories:
            category_query = Q()
            for category in institution_categories:
                # Handle both ID-based and value-based filtering (xususiy, davlat, xalqaro)
                if category.isdigit():
                    category_query |= Q(institution_category_id=category)
                else:
                    category_query |= Q(institution_category__name__icontains=category)
            queryset = queryset.filter(category_query)
        
        # Filter by location - support for multiple values
        locations = self.request.GET.getlist('location')
        if locations:
            location_query = Q()
            for location_id in locations:
                location_query |= Q(location_id=location_id)
            queryset = queryset.filter(location_query)
        
        # Filter by education type - support for multiple values
        education_types = self.request.GET.getlist('education_type')
        if education_types:
            education_type_query = Q()
            for edu_type_id in education_types:
                education_type_query |= Q(education_types__id=edu_type_id)
            queryset = queryset.filter(education_type_query)
        
        # Filter by education language - support for multiple values
        education_languages = self.request.GET.getlist('education_language')
        if education_languages:
            education_language_query = Q()
            for language_id in education_languages:
                education_language_query |= Q(education_languages__id=language_id)
            queryset = queryset.filter(education_language_query)
        
        # Filter by degree - support for multiple values
        degrees = self.request.GET.getlist('degree')
        if degrees:
            degree_query = Q()
            for degree_id in degrees:
                degree_query |= Q(degrees__id=degree_id)
            queryset = queryset.filter(degree_query)
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price and min_price.isdigit():
            queryset = queryset.filter(minimal_tuition_fee__gte=int(min_price))
        if max_price and max_price.isdigit():
            queryset = queryset.filter(maximal_tuition_fee__lte=int(max_price))
        
        # Filter by admission status
        admission_status = self.request.GET.get('admission_status')
        if admission_status == 'open':
            queryset = queryset.filter(is_open_for_admission=True)
        
        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options to context
        context['institution_categories'] = InstitutionCategory.objects.all()
        context['locations'] = Location.objects.all()
        context['education_types'] = EducationType.objects.all()
        context['education_languages'] = EducationLanguage.objects.all()
        context['degrees'] = Degree.objects.all()
        
        # Keep selected filters in context as lists for multiple selection support
        context['selected_filters'] = {
            'institution_category': self.request.GET.getlist('institution_category'),
            'location': self.request.GET.getlist('location'),
            'education_type': self.request.GET.getlist('education_type'),
            'education_language': self.request.GET.getlist('education_language'),
            'degree': self.request.GET.getlist('degree'),
            'admission_status': self.request.GET.get('admission_status'),
            'search': self.request.GET.get('search'),
            'min_price': self.request.GET.get('min_price'),
            'max_price': self.request.GET.get('max_price'),
        }
        
        return context


class DirectionListView(ListView):
    """View for listing educational directions with filters."""
    model = Direction
    template_name = 'universities/direction_list.html'
    context_object_name = 'directions'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Direction.objects.all()
        
        # Apply filters if present in GET parameters
        # Filter by university - support for multiple values
        universities = self.request.GET.getlist('university')
        if universities:
            university_query = Q()
            for uni_id in universities:
                university_query |= Q(university_id=uni_id)
            queryset = queryset.filter(university_query)
        
        # Filter by category - support for multiple values
        categories = self.request.GET.getlist('category')
        if categories:
            category_query = Q()
            for category_id in categories:
                category_query |= Q(category_id=category_id)
            queryset = queryset.filter(category_query)
        
        # Filter by education type - support for multiple values
        education_types = self.request.GET.getlist('education_type')
        if education_types:
            education_type_query = Q()
            for edu_type_id in education_types:
                education_type_query |= Q(education_types__id=edu_type_id)
            queryset = queryset.filter(education_type_query)
        
        # Filter by education language - support for multiple values
        education_languages = self.request.GET.getlist('education_language')
        if education_languages:
            education_language_query = Q()
            for language_id in education_languages:
                education_language_query |= Q(education_languages__id=language_id)
            queryset = queryset.filter(education_language_query)
        
        # Filter by degree - support for multiple values
        degrees = self.request.GET.getlist('degree')
        if degrees:
            degree_query = Q()
            for degree_id in degrees:
                degree_query |= Q(degrees__id=degree_id)
            queryset = queryset.filter(degree_query)
        
        # Filter by admission status
        admission_status = self.request.GET.get('admission_status')
        if admission_status == 'open':
            queryset = queryset.filter(is_open_for_admission=True)
        
        # Filter by search query
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(direction_name__icontains=search_query) | 
                Q(direction_description__icontains=search_query) |
                Q(university__full_name__icontains=search_query)
            )
            
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options to context
        context['universities'] = University.objects.all()
        context['categories'] = Category.objects.all()
        context['education_types'] = EducationType.objects.all()
        context['education_languages'] = EducationLanguage.objects.all()
        context['degrees'] = Degree.objects.all()
        
        # Keep selected filters in context as lists for multiple selection support
        context['selected_filters'] = {
            'university': self.request.GET.getlist('university'),
            'category': self.request.GET.getlist('category'),
            'education_type': self.request.GET.getlist('education_type'),
            'education_language': self.request.GET.getlist('education_language'),
            'degree': self.request.GET.getlist('degree'),
            'admission_status': self.request.GET.get('admission_status'),
            'search': self.request.GET.get('search'),
        }
        
        return context


class UniversityDetailView(DetailView):
    """View for displaying university details and programs."""
    model = University
    template_name = "universities/university_detail.html"
    context_object_name = "university"

    # --- helper -------------------------------------------------------------

    @staticmethod
    def _uzbek_date(d):
        """Return `1 Iyun 2025` style or '' if d is None."""
        if not d:
            return ""
        month = {
            1: "Yanvar", 2: "Fevral", 3: "Mart",    4: "Aprel",
            5: "May",    6: "Iyun",   7: "Iyul",    8: "Avgust",
            9: "Sentabr",10: "Oktabr",11: "Noyabr",12: "Dekabr",
        }[d.month]
        return f"{d.day} {month} {d.year}"

    # --- view ---------------------------------------------------------------

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # ❶ Directions/programs
        directions = (
            Direction.objects
            .filter(university=self.object)
            .order_by("direction_name")
            .prefetch_related("degrees")
        )
        ctx["directions"] = directions

        # Group directions by degree
        degree_groups = {}
        for direction in directions:
            degrees = direction.degrees.all()
            
            # If no degrees assigned, put in 'other'
            if not degrees:
                if 'other' not in degree_groups:
                    degree_groups['other'] = []
                degree_groups['other'].append(direction)
                continue
                
            # Otherwise, add to each matching degree group
            for degree in degrees:
                degree_key = degree.name.lower()
                # Normalize degree keys for common types
                if 'bakal' in degree_key:
                    degree_key = 'bachelor'
                elif 'magis' in degree_key:
                    degree_key = 'master'
                else:
                    degree_key = 'other'
                    
                if degree_key not in degree_groups:
                    degree_groups[degree_key] = []
                degree_groups[degree_key].append(direction)
        
        ctx["degrees"] = degree_groups

        # ❷ Admission period in Uzbek
        start = self._uzbek_date(self.object.admission_start_date)
        end   = self._uzbek_date(self.object.admission_deadline)

        if start and end:
            ctx["admission_period"] = f"{start} – {end}"
        elif start:
            ctx["admission_period"] = start
        elif end:
            ctx["admission_period"] = end
        else:
            ctx["admission_period"] = "Ma'lumot yo'q"

        # ❸ Tuition‑fee range
        min_fee, max_fee = self.object.minimal_tuition_fee, self.object.maximal_tuition_fee
        if min_fee and max_fee:
            ctx["tuition_fee_range"] = f"{min_fee:,} – {max_fee:,} UZS".replace(",", " ")
        elif min_fee:
            ctx["tuition_fee_range"] = f"{min_fee:,} UZS".replace(",", " ")
        else:
            ctx["tuition_fee_range"] = "Ma'lumot mavjud emas"
            
        ctx["back_url"] = (
            self.request.META.get("HTTP_REFERER") 
            if self.request.META.get("HTTP_REFERER") != self.request.build_absolute_uri() 
            and self.request.META.get("HTTP_REFERER") 
            else reverse("universities:university_list")
        )
        ctx["share_url"] = self.request.build_absolute_uri()

        return ctx


class DirectionDetailView(DetailView):
    """View for displaying direction/program details."""
    model = Direction
    template_name = "universities/direction_detail.html"
    context_object_name = "direction"
    slug_field = "direction_slug"
    slug_url_kwarg = "direction_slug"
    
    # --- helper -------------------------------------------------------------
    
    @staticmethod
    def _uzbek_date(d):
        """Return `1 Iyun 2025` style or '' if d is None."""
        if not d:
            return ""
        month = {
            1: "Yanvar", 2: "Fevral", 3: "Mart",    4: "Aprel",
            5: "May",    6: "Iyun",   7: "Iyul",    8: "Avgust",
            9: "Sentabr",10: "Oktabr",11: "Noyabr",12: "Dekabr",
        }[d.month]
        return f"{d.day} {month} {d.year}"
    
    # --- view ---------------------------------------------------------------
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # ❶ Application period in Uzbek
        start = self._uzbek_date(self.object.application_start_date)
        end = self._uzbek_date(self.object.application_deadline)
        
        if start and end:
            ctx["application_period"] = f"{start} – {end}"
        elif start:
            ctx["application_period"] = start
        elif end:
            ctx["application_period"] = end
        else:
            ctx["application_period"] = "Ma'lumot yo'q"
            
        ctx["back_url"] = (
            self.request.META.get("HTTP_REFERER") 
            if self.request.META.get("HTTP_REFERER") != self.request.build_absolute_uri() 
            and self.request.META.get("HTTP_REFERER") 
            else reverse("universities:direction_list")
        )
        ctx["share_url"] = self.request.build_absolute_uri()
        
        return ctx
