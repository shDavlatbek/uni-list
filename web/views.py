from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q, Count, Min, Max
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json

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


@method_decorator(cache_page(60 * 5), name='dispatch')  # Cache for 5 minutes
class UniversityListView(ListView):
    """Enhanced view for listing universities with optimized filters."""
    model = University
    template_name = 'universities/university_list.html'
    context_object_name = 'universities'
    paginate_by = 12
    
    def get_queryset(self):
        # Optimize with select_related and prefetch_related
        queryset = University.objects.select_related(
            'institution_category', 'location'
        ).prefetch_related(
            'education_types', 'education_languages', 'degrees', 'directions'
        )
        
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
                if location_id.isdigit():
                    location_query |= Q(location_id=location_id)
            queryset = queryset.filter(location_query)
        
        # Filter by education type - support for multiple values
        education_types = self.request.GET.getlist('education_type')
        if education_types:
            education_type_query = Q()
            for edu_type_id in education_types:
                if edu_type_id.isdigit():
                    education_type_query |= Q(education_types__id=edu_type_id)
            queryset = queryset.filter(education_type_query)
        
        # Filter by education language - support for multiple values
        education_languages = self.request.GET.getlist('education_language')
        if education_languages:
            education_language_query = Q()
            for language_id in education_languages:
                if language_id.isdigit():
                    education_language_query |= Q(education_languages__id=language_id)
            queryset = queryset.filter(education_language_query)
        
        # Filter by degree - support for multiple values
        degrees = self.request.GET.getlist('degree')
        if degrees:
            degree_query = Q()
            for degree_id in degrees:
                if degree_id.isdigit():
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
        
        # Filter by search query with full-text search simulation
        search_query = self.request.GET.get('search')
        if search_query:
            search_terms = search_query.split()
            search_q = Q()
            for term in search_terms:
                search_q |= (
                    Q(full_name__icontains=term) | 
                    Q(description__icontains=term) |
                    Q(location__name__icontains=term) |
                    Q(institution_category__name__icontains=term)
                )
            queryset = queryset.filter(search_q)
        
        # Add sorting options
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'name':
            queryset = queryset.order_by('full_name')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('minimal_tuition_fee')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-minimal_tuition_fee')
        elif sort_by == 'location':
            queryset = queryset.order_by('location__name', 'full_name')
        else:
            queryset = queryset.order_by('full_name')
            
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


# API Views for Dynamic Filtering

@require_http_methods(["GET"])
def university_filter_api(request):
    """
    API endpoint for dynamic university filtering without page reload.
    Returns JSON response with filtered universities and pagination info.
    """
    try:
        # Get the same queryset as UniversityListView
        queryset = University.objects.select_related(
            'institution_category', 'location'
        ).prefetch_related(
            'education_types', 'education_languages', 'degrees', 'directions'
        )
        
        # Apply the same filters as in UniversityListView
        # Filter by institution category
        institution_categories = request.GET.getlist('institution_category')
        if institution_categories:
            category_query = Q()
            for category in institution_categories:
                if category.isdigit():
                    category_query |= Q(institution_category_id=category)
                else:
                    category_query |= Q(institution_category__name__icontains=category)
            queryset = queryset.filter(category_query)
        
        # Filter by location
        locations = request.GET.getlist('location')
        if locations:
            location_query = Q()
            for location_id in locations:
                if location_id.isdigit():
                    location_query |= Q(location_id=location_id)
            queryset = queryset.filter(location_query)
        
        # Filter by education type
        education_types = request.GET.getlist('education_type')
        if education_types:
            education_type_query = Q()
            for edu_type_id in education_types:
                if edu_type_id.isdigit():
                    education_type_query |= Q(education_types__id=edu_type_id)
            queryset = queryset.filter(education_type_query)
        
        # Filter by education language
        education_languages = request.GET.getlist('education_language')
        if education_languages:
            education_language_query = Q()
            for language_id in education_languages:
                if language_id.isdigit():
                    education_language_query |= Q(education_languages__id=language_id)
            queryset = queryset.filter(education_language_query)
        
        # Filter by degree
        degrees = request.GET.getlist('degree')
        if degrees:
            degree_query = Q()
            for degree_id in degrees:
                if degree_id.isdigit():
                    degree_query |= Q(degrees__id=degree_id)
            queryset = queryset.filter(degree_query)
        
        # Filter by price range
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price and min_price.isdigit():
            queryset = queryset.filter(minimal_tuition_fee__gte=int(min_price))
        if max_price and max_price.isdigit():
            queryset = queryset.filter(maximal_tuition_fee__lte=int(max_price))
        
        # Filter by admission status
        admission_status = request.GET.get('admission_status')
        if admission_status == 'open':
            queryset = queryset.filter(is_open_for_admission=True)
        
        # Filter by search query
        search_query = request.GET.get('search')
        if search_query:
            search_terms = search_query.split()
            search_q = Q()
            for term in search_terms:
                search_q |= (
                    Q(full_name__icontains=term) | 
                    Q(description__icontains=term) |
                    Q(location__name__icontains=term) |
                    Q(institution_category__name__icontains=term)
                )
            queryset = queryset.filter(search_q)
        
        # Add sorting
        sort_by = request.GET.get('sort', 'name')
        if sort_by == 'name':
            queryset = queryset.order_by('full_name')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('minimal_tuition_fee')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-minimal_tuition_fee')
        elif sort_by == 'location':
            queryset = queryset.order_by('location__name', 'full_name')
        else:
            queryset = queryset.order_by('full_name')
        
        queryset = queryset.distinct()
        
        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 12) # Same as UniversityListView
        page_obj = paginator.page(page_number)
        
        # Serialize universities
        universities_data = []
        for university in page_obj:
            university_data = {
                'id': university.id,
                'full_name': university.full_name,
                'slug': university.slug,
                'logo_url': university.logo.url if university.logo else None,
                'description': university.description[:200] + '...' if university.description and len(university.description) > 200 else university.description,
                'location': university.location.name if university.location else None,
                'institution_category': university.institution_category.name if university.institution_category else None,
                'minimal_tuition_fee': university.minimal_tuition_fee,
                'maximal_tuition_fee': university.maximal_tuition_fee,
                'is_open_for_admission': university.is_open_for_admission,
                'has_grant': university.has_grant,
                'has_accomodation': university.has_accomodation,
                'admission_start_date': university.admission_start_date.strftime('%d %B %Y') if university.admission_start_date else None,
                'admission_deadline': university.admission_deadline.strftime('%d %B %Y') if university.admission_deadline else None,
                'directions_count': university.directions.count(),
                'detail_url': reverse('universities:university_detail', kwargs={'slug': university.slug}),
                'website': university.web_site,
            }
            universities_data.append(university_data)
        
        # Response data
        response_data = {
            'universities': universities_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            },
            'filters': {
                'total_active': len([v for values in request.GET.lists() for v in values if v and v != request.GET.get('page', '')]),
            },
            'success': True
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def direction_filter_api(request):
    """
    API endpoint for dynamic direction filtering without page reload.
    Returns JSON response with filtered directions and pagination info.
    """
    try:
        # Get the same queryset as DirectionListView
        queryset = Direction.objects.select_related(
            'university', 'category'
        ).prefetch_related(
            'education_types', 'education_languages', 'degrees', 'tuition_fees'
        )
        
        # Apply filters similar to DirectionListView
        # Filter by university
        universities = request.GET.getlist('university')
        if universities:
            university_query = Q()
            for uni_id in universities:
                if uni_id.isdigit():
                    university_query |= Q(university_id=uni_id)
            queryset = queryset.filter(university_query)
        
        # Filter by category
        categories = request.GET.getlist('category')
        if categories:
            category_query = Q()
            for category_id in categories:
                if category_id.isdigit():
                    category_query |= Q(category_id=category_id)
            queryset = queryset.filter(category_query)
        
        # Filter by education type
        education_types = request.GET.getlist('education_type')
        if education_types:
            education_type_query = Q()
            for edu_type_id in education_types:
                if edu_type_id.isdigit():
                    education_type_query |= Q(education_types__id=edu_type_id)
            queryset = queryset.filter(education_type_query)
        
        # Filter by education language
        education_languages = request.GET.getlist('education_language')
        if education_languages:
            education_language_query = Q()
            for language_id in education_languages:
                if language_id.isdigit():
                    education_language_query |= Q(education_languages__id=language_id)
            queryset = queryset.filter(education_language_query)
        
        # Filter by degree
        degrees = request.GET.getlist('degree')
        if degrees:
            degree_query = Q()
            for degree_id in degrees:
                if degree_id.isdigit():
                    degree_query |= Q(degrees__id=degree_id)
            queryset = queryset.filter(degree_query)
        
        # Filter by admission status
        admission_status = request.GET.get('admission_status')
        if admission_status == 'open':
            queryset = queryset.filter(is_open_for_admission=True)
        
        # Filter by search query
        search_query = request.GET.get('search')
        if search_query:
            search_terms = search_query.split()
            search_q = Q()
            for term in search_terms:
                search_q |= (
                    Q(direction_name__icontains=term) | 
                    Q(direction_description__icontains=term) |
                    Q(university__full_name__icontains=term) |
                    Q(category__name__icontains=term)
                )
            queryset = queryset.filter(search_q)
        
        queryset = queryset.distinct().order_by('university__full_name', 'direction_name')
        
        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(queryset, 10) # Same as DirectionListView
        page_obj = paginator.page(page_number)
        
        # Serialize directions
        directions_data = []
        for direction in page_obj:
            first_fee = direction.tuition_fees.first()
            direction_data = {
                'id': direction.id,
                'direction_name': direction.direction_name,
                'direction_slug': direction.direction_slug,
                'university_name': direction.university.full_name,
                'university_logo': direction.university.logo.url if direction.university.logo else None,
                'category': direction.category.name if direction.category else None,
                'description': direction.direction_description[:150] + '...' if direction.direction_description and len(direction.direction_description) > 150 else direction.direction_description,
                'has_stipend': direction.has_stipend,
                'is_open_for_admission': direction.is_open_for_admission,
                'application_deadline': direction.application_deadline.strftime('%d %B %Y') if direction.application_deadline else None,
                'tuition_fee': first_fee.local_tuition_fee if first_fee else None,
                'degrees': [degree.name for degree in direction.degrees.all()],
                'education_languages': [lang.name for lang in direction.education_languages.all()],
                'education_types': [edu_type.name for edu_type in direction.education_types.all()],
                'detail_url': reverse('universities:direction_detail', kwargs={'direction_slug': direction.direction_slug}),
            }
            directions_data.append(direction_data)
        
        # Response data
        response_data = {
            'directions': directions_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            },
            'success': True
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def filter_options_api(request):
    """
    API endpoint to get all available filter options.
    Used for populating filter dropdowns dynamically.
    """
    try:
        filter_type = request.GET.get('type', 'all')
        
        data = {}
        
        if filter_type in ['all', 'universities']:
            data.update({
                'institution_categories': [
                    {'id': cat.id, 'name': cat.name} 
                    for cat in InstitutionCategory.objects.all().order_by('name')
                ],
                'locations': [
                    {'id': loc.id, 'name': loc.name, 'university_count': loc.university_set.count()} 
                    for loc in Location.objects.annotate(
                        university_count=Count('university')
                    ).order_by('name')
                ],
                'education_types': [
                    {'id': et.id, 'name': et.name} 
                    for et in EducationType.objects.all().order_by('name')
                ],
                'education_languages': [
                    {'id': el.id, 'name': el.name} 
                    for el in EducationLanguage.objects.all().order_by('name')
                ],
                'degrees': [
                    {'id': deg.id, 'name': deg.name} 
                    for deg in Degree.objects.all().order_by('name')
                ],
            })
        
        if filter_type in ['all', 'directions']:
            data.update({
                'categories': [
                    {'id': cat.id, 'name': cat.name, 'direction_count': cat.direction_set.count()} 
                    for cat in Category.objects.annotate(
                        direction_count=Count('direction')
                    ).order_by('name')
                ],
                'universities': [
                    {'id': uni.id, 'name': uni.full_name, 'direction_count': uni.directions.count()} 
                    for uni in University.objects.annotate(
                        direction_count=Count('directions')
                    ).order_by('full_name')
                ],
            })
        
        # Add price range statistics
        if filter_type in ['all', 'universities']:
            price_stats = University.objects.aggregate(
                min_price=Min('minimal_tuition_fee'),
                max_price=Max('maximal_tuition_fee')
            )
            data['price_range'] = {
                'min': price_stats['min_price'] or 0,
                'max': price_stats['max_price'] or 100000000
            }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
