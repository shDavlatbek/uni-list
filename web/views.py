# views.py
from django.shortcuts import render, get_object_or_404 # Import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max # Import Q, Min, Max
from .models import University, Direction, InstitutionCategory, Location, Category, EducationType, EducationLanguage, Degree
import json
from decimal import Decimal # For handling potential price ranges

# Helper function to load filter options (Consider caching this)
def get_filter_options():
    """Loads filter options from models."""
    # Calculate min/max prices safely, providing defaults if no universities exist
    min_price_agg = University.objects.aggregate(min_fee=Min('minimal_tuition_fee'))
    max_price_agg = University.objects.aggregate(max_fee=Max('maximal_tuition_fee'))

    min_price = min_price_agg['min_fee'] if min_price_agg['min_fee'] is not None else 0
    # Ensure max_price is at least min_price, or a default if no unis exist
    max_price = max_price_agg['max_fee'] if max_price_agg['max_fee'] is not None else 100000000
    if max_price < min_price and University.objects.exists():
         max_price = min_price # Avoid max being less than min if data is sparse


    return {
        'institution_categories': InstitutionCategory.objects.all().order_by('name'),
        'locations': Location.objects.all().order_by('name'),
        'categories': Category.objects.all().order_by('name'),
        'education_types': EducationType.objects.all().order_by('name'),
        'education_languages': EducationLanguage.objects.all().order_by('name'),
        'degrees': Degree.objects.all().order_by('name'), # Assuming you populate Degree model
        'min_price': min_price,
        'max_price': max_price,
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
    # No 'elif false' needed unless you specifically want to exclude nulls

    has_accomodation = filters.get('has_accomodation') # Assuming filter name
    if has_accomodation == 'true':
        universities = universities.filter(has_accomodation=True)

    # Price Range Filter
    min_price_str = filters.get('min_price')
    max_price_str = filters.get('max_price')
    if min_price_str:
        try:
            # Check non-null minimal fee >= min_price OR non-null maximal fee >= min_price
            universities = universities.filter(
                Q(minimal_tuition_fee__isnull=False, minimal_tuition_fee__gte=Decimal(min_price_str)) |
                Q(maximal_tuition_fee__isnull=False, maximal_tuition_fee__gte=Decimal(min_price_str))
            ).distinct()
        except (ValueError, TypeError):
            pass # Ignore invalid input
    if max_price_str:
        try:
             # Check non-null minimal fee <= max_price
            universities = universities.filter(
                 minimal_tuition_fee__isnull=False, minimal_tuition_fee__lte=Decimal(max_price_str)
            ).distinct()
        except (ValueError, TypeError):
            pass # Ignore invalid input


    # --- Pagination ---
    paginator = Paginator(universities.order_by('full_name'), 15) # Show 15 universities per page, ensure consistent order
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
            Q(direction_name__icontains=query) |
            Q(university__full_name__icontains=query)
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

    # Price Range Filter (Filtering based on the University's overall price range)
    min_price_str = filters.get('min_price')
    max_price_str = filters.get('max_price')
    if min_price_str:
        try:
            directions = directions.filter(
                 Q(university__minimal_tuition_fee__isnull=False, university__minimal_tuition_fee__gte=Decimal(min_price_str)) |
                 Q(university__maximal_tuition_fee__isnull=False, university__maximal_tuition_fee__gte=Decimal(min_price_str))
            ).distinct()
        except (ValueError, TypeError):
            pass
    if max_price_str:
        try:
            directions = directions.filter(
                university__minimal_tuition_fee__isnull=False, university__minimal_tuition_fee__lte=Decimal(max_price_str)
            ).distinct()
        except (ValueError, TypeError):
            pass

    # --- Pagination ---
    paginator = Paginator(directions.order_by('university__full_name', 'direction_name'), 20) # Show 20 directions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get filter options (can reuse or create a specific one for directions)
    # Need to add University list for filtering by university
    filter_options = get_filter_options()
    # Add distinct list of universities present in the current filtered directions
    # This makes the university filter dropdown more relevant to the current search
    current_uni_ids = directions.values_list('university__id', flat=True).distinct()
    filter_options['universities'] = University.objects.filter(id__in=current_uni_ids).order_by('full_name')


    context = {
        'page_obj': page_obj,
        'filter_options': filter_options,
        'applied_filters': request.GET,
    }
    return render(request, 'direction_list.html', context)

# --- Detail Views ---

def university_detail(request, slug):
    """Displays details for a single university."""
    university = get_object_or_404(
        University.objects.select_related('location', 'institution_category')
                          .prefetch_related('education_types', 'education_languages', 'degrees', 'directions__category', 'directions__education_types', 'directions__education_languages'), # Prefetch related directions and their fields
        slug=slug
    )
    # Get related directions, ordered
    related_directions = university.directions.order_by('direction_name').all()

    context = {
        'university': university,
        'directions': related_directions, # Pass directions to the context
    }
    return render(request, 'university_detail.html', context)


def direction_detail(request, slug):
    """Displays details for a single direction."""
    direction = get_object_or_404(
        Direction.objects.select_related('university__location', 'university__institution_category', 'category') # Select related university details
                       .prefetch_related('education_types', 'education_languages', 'degrees'), # Prefetch direction's own M2M fields
        direction_slug=slug # Filter by direction_slug
    )
    context = {
        'direction': direction,
    }
    return render(request, 'direction_detail.html', context)

