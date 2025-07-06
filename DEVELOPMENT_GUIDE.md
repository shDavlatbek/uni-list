# Development Guide - University Directory Project

## 🚀 Enhanced Features Implementation

This guide documents the improvements made to the university directory project, including dynamic filtering, template tags, and API endpoints.

## 📋 Table of Contents

1. [New Template Tags](#template-tags)
2. [API Endpoints](#api-endpoints)  
3. [Enhanced Views](#enhanced-views)
4. [Dynamic Filtering System](#dynamic-filtering)
5. [Performance Optimizations](#performance)
6. [Usage Examples](#usage-examples)

## 🏷️ Template Tags

### Overview
Custom template tags have been created to make filtering components reusable and consistent across templates.

### Location
- **File:** `web/templatetags/filter_tags.py`
- **Templates:** `templates/includes/`

### Available Tags

#### 1. `checkbox_filter`
Creates a reusable checkbox filter group.

```django
{% load filter_tags %}

{% checkbox_filter "Location" "location" locations selected_filters.location "fas fa-map-marker-alt" %}
```

**Parameters:**
- `title`: Display title for the filter group
- `field_name`: HTML input name attribute  
- `options`: Queryset or list of options
- `selected_values`: Currently selected values
- `icon_class`: FontAwesome icon class
- `collapsible`: Whether section should be collapsible (default: True)

#### 2. `search_filter`
Creates a search input with button.

```django
{% search_filter placeholder="Search universities..." value=selected_filters.search %}
```

#### 3. `price_range_filter`
Creates a price range slider with noUiSlider.

```django
{% price_range_filter selected_min=selected_filters.min_price selected_max=selected_filters.max_price %}
```

#### 4. `filter_count`
Displays formatted count of results.

```django
{% filter_count page_obj.paginator.count %}
```

#### 5. `filter_summary`
Shows active filters with remove buttons.

```django
{% filter_summary %}
```

#### 6. `pagination_url`
Generates pagination URLs preserving query parameters.

```django
{% pagination_url page_number %}
```

### Usage in Templates

```django
{% extends 'base.html' %}
{% load filter_tags %}

<form method="get" id="filters-form">
    <!-- Search -->
    {% search_filter placeholder="University name..." value=selected_filters.search %}
    
    <!-- Checkboxes -->
    {% checkbox_filter "Location" "location" locations selected_filters.location "fas fa-map-marker-alt" %}
    
    <!-- Price Range -->
    {% price_range_filter selected_min=selected_filters.min_price selected_max=selected_filters.max_price %}
    
    <!-- Active Filters -->
    {% filter_summary %}
</form>

<!-- Results Count -->
<h5>{% filter_count page_obj.paginator.count %}</h5>
```

## 🔌 API Endpoints

### Overview
RESTful API endpoints for dynamic filtering without page reloads.

### Endpoints

#### 1. University Filter API
**URL:** `/api/universities/filter/`  
**Method:** GET  
**Description:** Returns filtered universities with pagination

**Parameters:**
- `institution_category[]`: Institution type IDs or names
- `location[]`: Location IDs
- `education_type[]`: Education type IDs
- `education_language[]`: Language IDs
- `degree[]`: Degree IDs
- `min_price`: Minimum price
- `max_price`: Maximum price
- `admission_status`: 'open' for open admissions only
- `search`: Search query
- `sort`: Sorting option ('name', 'price_low', 'price_high', 'location')
- `page`: Page number

**Response Format:**
```json
{
    "success": true,
    "universities": [
        {
            "id": 1,
            "full_name": "University Name",
            "slug": "university-slug",
            "logo_url": "/media/logos/logo.jpg",
            "location": "Tashkent",
            "institution_category": "Private",
            "minimal_tuition_fee": 5000000,
            "maximal_tuition_fee": 15000000,
            "is_open_for_admission": true,
            "has_grant": true,
            "directions_count": 25,
            "detail_url": "/universities/university-slug/"
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 5,
        "total_count": 60,
        "has_previous": false,
        "has_next": true
    },
    "filters": {
        "total_active": 3
    }
}
```

#### 2. Direction Filter API
**URL:** `/api/directions/filter/`  
**Method:** GET  
**Description:** Returns filtered directions with pagination

**Parameters:**
- `university[]`: University IDs
- `category[]`: Category IDs
- `education_type[]`: Education type IDs
- `education_language[]`: Language IDs
- `degree[]`: Degree IDs
- `admission_status`: 'open' for open admissions
- `search`: Search query
- `page`: Page number

#### 3. Filter Options API
**URL:** `/api/filter-options/`  
**Method:** GET  
**Description:** Returns all available filter options

**Parameters:**
- `type`: 'all', 'universities', or 'directions'

**Response:**
```json
{
    "success": true,
    "data": {
        "locations": [
            {"id": 1, "name": "Tashkent", "university_count": 45}
        ],
        "institution_categories": [
            {"id": 1, "name": "Private"}
        ],
        "price_range": {
            "min": 1000000,
            "max": 50000000
        }
    }
}
```

## 🎯 Enhanced Views

### Performance Optimizations

#### 1. Database Optimization
```python
@method_decorator(cache_page(60 * 5), name='dispatch')  # 5-minute cache
class UniversityListView(ListView):
    def get_queryset(self):
        # Optimized with select_related and prefetch_related
        return University.objects.select_related(
            'institution_category', 'location'
        ).prefetch_related(
            'education_types', 'education_languages', 'degrees', 'directions'
        )
```

#### 2. Enhanced Search
- Split search terms for better matching
- Search across multiple related fields
- Input validation for numeric filters

#### 3. Sorting Options
- Sort by name, price (low to high), price (high to low), location
- Maintained in both views and API endpoints

## 🔄 Dynamic Filtering System

### JavaScript Architecture

#### Core Features
- AJAX-based filtering without page reloads
- Debounced input handling (500ms delay)
- Price range slider integration
- URL state management with browser history
- Error handling and loading states
- Smooth animations and transitions

#### Usage

```html
<!-- Include required libraries -->
<script src="https://cdn.jsdelivr.net/npm/nouislider@14.6.3/distribute/nouislider.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/nouislider@14.6.3/distribute/nouislider.min.css">

<!-- Initialize filter system -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    window.filterSystem = new DynamicFilterSystem({
        // Configuration options
        debounceDelay: 500,
        enableAjax: true,
        enableHistory: true,
        
        // Callbacks
        onFilterStart: () => console.log('Filtering started'),
        onFilterComplete: (data) => console.log('Results:', data),
        onError: (error) => console.error('Error:', error)
    });
});
</script>
```

#### Key Methods

```javascript
// Submit filters programmatically
filterSystem.submitFilters(pageNumber);

// Clear all active filters
filterSystem.clearAllFilters();

// Apply filters from URL state
filterSystem.applyFiltersFromState(queryString);
```

## ⚡ Performance Optimizations

### Database Level
1. **Query Optimization**
   - `select_related()` for foreign keys
   - `prefetch_related()` for many-to-many relationships
   - `distinct()` to prevent duplicates

2. **Caching**
   - View-level caching (5 minutes)
   - Template fragment caching for filter options
   - Browser caching for static assets

3. **Indexing**
   - Database indexes on frequently filtered fields
   - Full-text search indexes (for production)

### Frontend Level
1. **Debounced Inputs**
   - 500ms delay for search inputs
   - Immediate submission for checkboxes and selects

2. **Progressive Enhancement**
   - Works without JavaScript (form submission fallback)
   - AJAX enhancement when available

3. **Lazy Loading**
   - Images loaded on demand
   - Pagination for large result sets

## 📚 Usage Examples

### 1. Adding New Filter Type

#### Step 1: Add to Model (if needed)
```python
class University(models.Model):
    # ... existing fields ...
    new_field = models.CharField(max_length=100)
```

#### Step 2: Update View
```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    # Add new filter
    new_filter = self.request.GET.getlist('new_field')
    if new_filter:
        queryset = queryset.filter(new_field__in=new_filter)
    
    return queryset

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['new_field_options'] = NewFieldModel.objects.all()
    return context
```

#### Step 3: Update Template
```django
{% checkbox_filter "New Field" "new_field" new_field_options selected_filters.new_field "fas fa-icon" %}
```

#### Step 4: Update API (if using AJAX)
```python
def university_filter_api(request):
    # ... existing code ...
    
    new_field = request.GET.getlist('new_field')
    if new_field:
        queryset = queryset.filter(new_field__in=new_field)
```

### 2. Custom Filter Component

#### Create Template Include
```django
<!-- templates/includes/custom_filter.html -->
<div class="mb-4 pb-3 border-bottom">
    <label class="form-label fw-bold mb-3">{{ title }}</label>
    <!-- Custom filter content -->
</div>
```

#### Create Template Tag
```python
@register.inclusion_tag('includes/custom_filter.html')
def custom_filter(title, options, selected):
    return {
        'title': title,
        'options': options,
        'selected': selected
    }
```

### 3. Adding Sorting Options

#### Update View
```python
def get_queryset(self):
    queryset = super().get_queryset()
    
    sort_by = self.request.GET.get('sort', 'name')
    sort_options = {
        'name': 'full_name',
        'date': '-created_at',
        'popularity': '-view_count'
    }
    
    if sort_by in sort_options:
        queryset = queryset.order_by(sort_options[sort_by])
    
    return queryset
```

#### Update Template
```django
<select name="sort" class="form-select">
    <option value="name" {% if request.GET.sort == 'name' %}selected{% endif %}>Name</option>
    <option value="date" {% if request.GET.sort == 'date' %}selected{% endif %}>Date</option>
    <option value="popularity" {% if request.GET.sort == 'popularity' %}selected{% endif %}>Popularity</option>
</select>
```

## 🛠️ Development Workflow

### 1. Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create test data
python manage.py loaddata fixtures/test_data.json

# Run development server
python manage.py runserver
```

### 2. Testing Filters
```bash
# Test university API
curl "http://localhost:8000/api/universities/filter/?location=1&search=test"

# Test directions API  
curl "http://localhost:8000/api/directions/filter/?university=1&category=2"

# Test filter options
curl "http://localhost:8000/api/filter-options/?type=universities"
```

### 3. Production Deployment
1. Set up Redis for caching
2. Configure PostgreSQL for better search
3. Enable compression and minification
4. Set up CDN for static files

## 🔧 Troubleshooting

### Common Issues

#### 1. Slider Not Working
- Ensure noUiSlider library is loaded
- Check for JavaScript errors in console
- Verify slider element exists in DOM

#### 2. AJAX Requests Failing
- Check API endpoint URLs
- Verify CSRF token handling
- Check network requests in browser dev tools

#### 3. Filters Not Preserving State
- Ensure form field names match exactly
- Check URL parameter parsing
- Verify template tag usage

### Debug Mode
```python
# In views.py, add debug logging
import logging
logger = logging.getLogger(__name__)

def get_queryset(self):
    queryset = super().get_queryset()
    logger.debug(f"Filter parameters: {self.request.GET}")
    logger.debug(f"Queryset count: {queryset.count()}")
    return queryset
```

---

## 📞 Support

For questions or issues with the enhanced filtering system:

1. Check this documentation first
2. Review the code comments in the relevant files
3. Test with browser developer tools
4. Check Django logs for errors

The system is designed to be robust and fall back gracefully when JavaScript is disabled, ensuring accessibility and compatibility across different environments. 