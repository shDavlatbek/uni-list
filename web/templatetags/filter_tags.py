from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import json

register = template.Library()


@register.inclusion_tag('includes/filter_checkbox_group.html')
def checkbox_filter(title, field_name, options, selected_values, icon_class="fas fa-filter", collapsible=True):
    """
    Render a group of checkboxes for filtering.
    
    Args:
        title: Display title for the filter group
        field_name: HTML input name attribute
        options: Queryset or list of options with 'id' and 'name' attributes
        selected_values: List of currently selected values
        icon_class: FontAwesome icon class
        collapsible: Whether the section should be collapsible
    """
    return {
        'title': title,
        'field_name': field_name,
        'options': options,
        'selected_values': [str(v) for v in selected_values] if selected_values else [],
        'icon_class': icon_class,
        'collapsible': collapsible,
        'collapse_id': f"{field_name}Collapse"
    }


@register.inclusion_tag('includes/filter_search_input.html')
def search_filter(placeholder="Qidirish...", value="", field_name="search", title=""):
    """
    Render a search input with button.
    
    Args:
        placeholder: Input placeholder text
        value: Current search value
        field_name: HTML input name attribute
        title: Label title (optional)
    """
    return {
        'placeholder': placeholder,
        'value': value or '',
        'field_name': field_name,
        'title': title
    }


@register.inclusion_tag('includes/filter_price_range.html')
def price_range_filter(min_value=0, max_value=100000000, selected_min=None, selected_max=None):
    """
    Render a price range slider.
    
    Args:
        min_value: Minimum possible value
        max_value: Maximum possible value
        selected_min: Currently selected minimum value
        selected_max: Currently selected maximum value
    """
    return {
        'min_value': min_value,
        'max_value': max_value,
        'selected_min': selected_min or min_value,
        'selected_max': selected_max or max_value
    }


@register.simple_tag
def filter_count(queryset_or_count):
    """
    Display formatted count of results.
    
    Args:
        queryset_or_count: Queryset with count() method or integer
    """
    try:
        if hasattr(queryset_or_count, 'count'):
            count = queryset_or_count.count()
        else:
            count = int(queryset_or_count)
        
        if count == 0:
            return "Natija topilmadi"
        elif count == 1:
            return "1 ta natija"
        else:
            return f"{count:,} ta natija".replace(',', ' ')
    except (ValueError, TypeError):
        return "0 ta natija"


@register.simple_tag(takes_context=True)
def pagination_url(context, page_number):
    """
    Generate pagination URL preserving all query parameters.
    
    Args:
        context: Template context
        page_number: Target page number
    """
    request = context['request']
    query_dict = request.GET.copy()
    query_dict['page'] = page_number
    return f"?{query_dict.urlencode()}"


@register.simple_tag(takes_context=True)
def active_filters_count(context):
    """
    Count number of active filters (excluding page and search).
    
    Args:
        context: Template context with request
    """
    request = context['request']
    exclude_params = {'page', 'search'}
    
    count = 0
    for key, values in request.GET.lists():
        if key not in exclude_params:
            if isinstance(values, list):
                count += len([v for v in values if v])
            elif values:
                count += 1
    
    return count


@register.simple_tag(takes_context=True)
def clear_filters_url(context, keep_search=False):
    """
    Generate URL with all filters cleared.
    
    Args:
        context: Template context
        keep_search: Whether to preserve search parameter
    """
    request = context['request']
    
    if keep_search and request.GET.get('search'):
        return f"?search={request.GET.get('search')}"
    
    return request.path


@register.filter
def get_selected_names(options, selected_ids):
    """
    Get names of selected options for display.
    
    Args:
        options: Queryset or list of options
        selected_ids: List of selected IDs
    """
    if not selected_ids:
        return []
    
    selected_ids = [str(sid) for sid in selected_ids]
    names = []
    
    for option in options:
        if str(option.id) in selected_ids:
            names.append(option.name)
    
    return names


@register.inclusion_tag('includes/filter_summary.html', takes_context=True)
def filter_summary(context):
    """
    Display summary of active filters with remove buttons.
    
    Args:
        context: Template context
    """
    request = context['request']
    active_filters = []
    
    # Get filter context data (assuming it's passed from view)
    filter_options = {
        'institution_categories': context.get('institution_categories', []),
        'locations': context.get('locations', []),
        'education_types': context.get('education_types', []),
        'education_languages': context.get('education_languages', []),
        'degrees': context.get('degrees', []),
        'universities': context.get('universities', []),
        'categories': context.get('categories', []),
    }
    
    # Map URL parameters to human-readable names
    param_mapping = {
        'institution_category': ('OTM turi', filter_options['institution_categories']),
        'location': ('Manzil', filter_options['locations']),
        'education_type': ('Ta\'lim turi', filter_options['education_types']),
        'education_language': ('Ta\'lim tili', filter_options['education_languages']),
        'degree': ('Daraja', filter_options['degrees']),
        'university': ('Universitet', filter_options['universities']),
        'category': ('Yo\'nalish', filter_options['categories']),
    }
    
    for param, values in request.GET.lists():
        if param in param_mapping and values:
            title, options = param_mapping[param]
            selected_names = get_selected_names(options, values)
            
            for value, name in zip(values, selected_names):
                # Create URL without this specific filter
                new_query = request.GET.copy()
                current_values = new_query.getlist(param)
                if value in current_values:
                    current_values.remove(value)
                
                if current_values:
                    new_query.setlist(param, current_values)
                else:
                    new_query.pop(param, None)
                
                remove_url = f"?{new_query.urlencode()}" if new_query else request.path
                
                active_filters.append({
                    'title': title,
                    'name': name,
                    'remove_url': remove_url
                })
    
    # Handle special filters
    if request.GET.get('min_price') or request.GET.get('max_price'):
        min_p = request.GET.get('min_price', '0')
        max_p = request.GET.get('max_price', '∞')
        
        new_query = request.GET.copy()
        new_query.pop('min_price', None)
        new_query.pop('max_price', None)
        remove_url = f"?{new_query.urlencode()}" if new_query else request.path
        
        active_filters.append({
            'title': 'Narx oralig\'i',
            'name': f"{min_p} - {max_p} UZS",
            'remove_url': remove_url
        })
    
    if request.GET.get('admission_status') == 'open':
        new_query = request.GET.copy()
        new_query.pop('admission_status', None)
        remove_url = f"?{new_query.urlencode()}" if new_query else request.path
        
        active_filters.append({
            'title': 'Qabul holati',
            'name': 'Faqat ochiq qabullar',
            'remove_url': remove_url
        })
    
    # Get clear filters URL
    request = context['request']
    if request.GET.get('search'):
        clear_url = f"?search={request.GET.get('search')}"
    else:
        clear_url = request.path
    
    return {
        'active_filters': active_filters,
        'total_count': len(active_filters),
        'clear_filters_url': clear_url
    }


@register.simple_tag
def json_encode(data):
    """
    JSON encode data for JavaScript consumption.
    
    Args:
        data: Python data structure to encode
    """
    return mark_safe(json.dumps(data)) 