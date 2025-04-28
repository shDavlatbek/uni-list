# views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import University, Direction, InstitutionCategory, Location, Category, EducationType, EducationLanguage, Degree
import json
from django.db import models
from decimal import Decimal # For handling potential price ranges

# Helper function to load filter options (Consider caching this)
def get_filter_options():
    """Loads filter options from models."""
    return {
        'institution_categories': InstitutionCategory.objects.all().order_by('name'),
        'locations': Location.objects.all().order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'education_types': EducationType.objects.all().order_by('name'),
        'education_languages': EducationLanguage.objects.all().order_by('name'),
        'degrees': Degree.objects.all().order_by('name'), # Assuming you populate Degree model
        # Add min/max price logic if needed based on actual data
        'min_price': University.objects.aggregate(models.Min('minimal_tuition_fee'))['minimal_tuition_fee__min'] or 0,
        'max_price': University.objects.aggregate(models.Max('maximal_tuition_fee'))['maximal_tuition_fee__max'] or 100000000,
    }

def university_list(request):
    """Displays a list of universities with filters."""
    universities = University.objects.select_related(
        'institution_category', 'location'
    ).prefetch_related(
        'education_types', 'education_languages', 'degrees'
    ).all()

    # --- Filtering Logic ---
    filters = request.GET.copy() # Use .copy() to make it mutable if needed

    # Text search
    query = filters.get('query')
    if query:
        universities = universities.filter(full_name__icontains=query)

    # ID-based filters (Many-to-Many)
    edu_type_ids = filters.getlist('edu_type')
    if edu_type_ids:
        universities = universities.filter(education_types__id__in=edu_type_ids).distinct()

    edu_lang_ids = filters.getlist('edu_lang')
    if edu_lang_ids:
        universities = universities.filter(education_languages__id__in=edu_lang_ids).distinct()

    degree_ids = filters.getlist('degree') # Assuming filter name 'degree'
    if degree_ids:
         universities = universities.filter(degrees__id__in=degree_ids).distinct()

    # ID-based filters (Foreign Key)
    inst_cat_id = filters.get('institution_category_id')
    if inst_cat_id:
        universities = universities.filter(institution_category__id=inst_cat_id)

    loc_id = filters.get('location')
    if loc_id:
        universities = universities.filter(location__id=loc_id)

    # Boolean filters
    has_grant = filters.get('has_grant')
    if has_grant == 'true':
        universities = universities.filter(has_grant=True)
    elif has_grant == 'false':
         universities = universities.filter(has_grant=False) # Or handle nulls if needed

    has_accomodation = filters.get('has_accomodation') # Assuming filter name
    if has_accomodation == 'true':
        universities = universities.filter(has_accomodation=True)
    elif has_accomodation == 'false':
        universities = universities.filter(has_accomodation=False)

    # Price Range Filter
    min_price = filters.get('min_price')
    max_price = filters.get('max_price')
    if min_price:
        try:
            universities = universities.filter(minimal_tuition_fee__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass # Ignore invalid input
    if max_price:
        try:
            # Use maximal_tuition_fee for the upper bound check
            universities = universities.filter(maximal_tuition_fee__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass # Ignore invalid input

    # --- Pagination ---
    paginator = Paginator(universities, 15) # Show 15 universities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_options': get_filter_options(),
        'applied_filters': request.GET, # Pass applied filters back to template
    }
    return render(request, 'university_list.html', context)


def direction_list(request):
    """Displays a list of directions with filters."""
    directions = Direction.objects.select_related(
        'university', 'category', 'university__location', 'university__institution_category'
    ).prefetch_related(
        'education_types', 'education_languages', 'degrees'
    ).all()

    # --- Filtering Logic ---
    filters = request.GET.copy()

    # Text search (on direction name or university name)
    query = filters.get('query')
    if query:
        directions = directions.filter(
            models.Q(direction_name__icontains=query) |
            models.Q(university__full_name__icontains=query)
        )

    # University Filter
    uni_id = filters.get('university_id')
    if uni_id:
        directions = directions.filter(university__id=uni_id)

    # ID-based filters (Many-to-Many on Direction)
    edu_type_ids = filters.getlist('edu_type')
    if edu_type_ids:
        directions = directions.filter(education_types__id__in=edu_type_ids).distinct()

    edu_lang_ids = filters.getlist('edu_lang')
    if edu_lang_ids:
        directions = directions.filter(education_languages__id__in=edu_lang_ids).distinct()

    degree_ids = filters.getlist('degree')
    if degree_ids:
         directions = directions.filter(degrees__id__in=degree_ids).distinct()

    # ID-based filters (Foreign Key on Direction)
    cat_id = filters.get('category')
    if cat_id:
        directions = directions.filter(category__id=cat_id)

    # Filters inherited from University (apply to the related university)
    inst_cat_id = filters.get('institution_category_id')
    if inst_cat_id:
        directions = directions.filter(university__institution_category__id=inst_cat_id)

    loc_id = filters.get('location')
    if loc_id:
        directions = directions.filter(university__location__id=loc_id)

    # Boolean filters
    has_stipend = filters.get('has_stipend')
    if has_stipend == 'true':
        directions = directions.filter(has_stipend=True)
    elif has_stipend == 'false':
         directions = directions.filter(has_stipend=False)

    # Price Range Filter (Needs refinement based on how tuition_fees is stored/queried)
    # This example assumes you might filter based on the University's overall price range
    # A more accurate filter would parse the 'tuition_fees' JSON if stored.
    min_price = filters.get('min_price')
    max_price = filters.get('max_price')
    if min_price:
        try:
             # Example: Filter if ANY tuition fee is >= min_price (requires JSON parsing or different model)
             # Or filter based on university's min fee:
             directions = directions.filter(university__minimal_tuition_fee__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
             # Example: Filter if ANY tuition fee is <= max_price (requires JSON parsing or different model)
             # Or filter based on university's max fee:
             directions = directions.filter(university__maximal_tuition_fee__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass

    # --- Pagination ---
    paginator = Paginator(directions, 20) # Show 20 directions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options (can reuse or create a specific one for directions)
    # Need to add University list for filtering by university
    filter_options = get_filter_options()
    filter_options['universities'] = University.objects.all().order_by('full_name')


    context = {
        'page_obj': page_obj,
        'filter_options': filter_options,
        'applied_filters': request.GET,
    }
    return render(request, 'direction_list.html', context)

# Add detail views if needed
# def university_detail(request, slug):
#     ...
# def direction_detail(request, slug):
#     ...
