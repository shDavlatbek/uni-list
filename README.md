# University Directory Project

## 🎓 Overview

A comprehensive Django web application for managing and displaying universities and educational directions in Uzbekistan. This platform allows users to discover universities, filter educational programs, and find detailed information about admission requirements and tuition fees.

## 🏗️ Architecture

### Project Structure
```
uni-list/
├── config/                 # Django project settings
│   ├── settings.py        # Main configuration
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI application
├── web/                   # Main application
│   ├── models.py         # Data models
│   ├── views.py          # View logic
│   ├── admin.py          # Admin configuration
│   └── urls.py           # App URL patterns
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   └── universities/     # University-specific templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded files
└── manage.py             # Django management script
```

## 📊 Data Models

### Core Models

#### University
Primary model representing educational institutions:
```python
- full_name: CharField(255) - University name
- slug: SlugField - URL-friendly identifier
- logo: FileField - University logo
- description: RichTextField - Institution description
- location: ForeignKey(Location) - Geographic location
- institution_category: ForeignKey(InstitutionCategory) - Type (Private/State/International)
- admission_start_date/admission_deadline: DateTimeField - Admission period
- minimal_tuition_fee/maximal_tuition_fee: PositiveIntegerField - Fee range
- is_open_for_admission: BooleanField - Current admission status
- Many-to-many relationships: education_types, education_languages, degrees
```

#### Direction
Educational programs offered by universities:
```python
- university: ForeignKey(University) - Parent institution
- direction_name: CharField(255) - Program name
- direction_slug: SlugField - URL identifier
- category: ForeignKey(Category) - Program category
- direction_description: RichTextField - Program details
- application_start_date/application_deadline: DateTimeField - Application period
- is_open_for_admission: BooleanField - Current status
- Many-to-many relationships: education_types, education_languages, degrees
```

#### TuitionFee
Detailed fee structure for programs:
```python
- direction: ForeignKey(Direction) - Associated program
- education_type: ForeignKey(EducationType) - Study mode
- local_tuition_fee: PositiveIntegerField - Local student fee
- international_tuition_fee: PositiveIntegerField - International student fee
- academic_year: CharField(9) - Year (e.g., "2024/25")
```

### Filter Models
- **InstitutionCategory**: Private/State/International classifications
- **Location**: Geographic regions/cities
- **Category**: Educational field categories (IT, Medicine, etc.)
- **EducationType**: Study modes (Full-time, Part-time, etc.)
- **EducationLanguage**: Languages of instruction
- **Degree**: Academic levels (Bachelor, Master, etc.)

## 🎛️ Features

### 1. University Listing (`/universities/`)
- **Advanced Filtering**:
  - Institution type (Private/State/International)
  - Location (multiple selection)
  - Education type, language, degree
  - Price range with slider
  - Search by name/description
  - Admission status filter

- **Dynamic UI**:
  - Auto-submit forms on filter changes
  - Collapsible filter sections
  - Pagination with query preservation
  - Responsive card layout

### 2. Direction Listing (`/directions/`)
- **Comprehensive Filtering**:
  - University selection
  - Program categories
  - Education type, language, degree
  - Admission status
  - Search functionality

### 3. Detail Views
- **University Details**: Full information, gallery, programs by degree
- **Direction Details**: Program specifics, requirements, application info

### 4. Admin Interface
- **Jazzmin Theme**: Modern, user-friendly interface
- **Nested Admin**: Manage universities with inline directions and fees
- **Rich Text Editing**: CKEditor integration for descriptions

## 🔧 Technical Implementation

### Views Architecture
```python
# Class-based views with sophisticated filtering
class UniversityListView(ListView):
    - Multi-parameter filtering with Q objects
    - Query string preservation for pagination
    - Context data for filter options
    
class DirectionListView(ListView):
    - Similar filtering architecture
    - University-specific filtering
    
# Detail views with computed context
class UniversityDetailView(DetailView):
    - Dynamic admission period formatting
    - Tuition fee range calculation
    - Program grouping by degree
```

### Template System
- **Base Template**: Common layout, navigation, footer
- **Dynamic Filtering**: JavaScript-enhanced form submission
- **Responsive Design**: Bootstrap 5 with mobile-first approach
- **Price Slider**: noUiSlider integration for range selection

### Key JavaScript Features
```javascript
// Auto-submit filtering
filterCheckboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        document.getElementById('filters-form').submit();
    });
});

// Price range slider with real-time updates
priceSlider.noUiSlider.on('end', function() {
    document.getElementById('filters-form').submit();
});
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2
- SQLite (development) / PostgreSQL (production)

### Installation Steps
```bash
# Clone repository
git clone <repository-url>
cd uni-list

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Dependencies
```
Django==5.2
django-ckeditor==6.7.2          # Rich text editing
django-cleanup==9.0.0           # File cleanup
django-jazzmin==3.0.1           # Admin theme
django-nested-admin==4.1.1      # Nested admin forms
gunicorn                         # Production server
```

## 📝 Usage Guide

### For Administrators
1. **Access Admin**: `/admin/` with superuser credentials
2. **Add Universities**: Use nested admin to add directions and fees
3. **Manage Categories**: Set up institution types, locations, categories
4. **Upload Media**: Add logos and gallery images

### For Developers
1. **Extend Models**: Add new fields or relationships as needed
2. **Custom Filters**: Modify `get_queryset()` methods in views
3. **Template Customization**: Override templates in `templates/` directory
4. **Static Files**: Add CSS/JS to `assets/` directory

### For AI Integration
This codebase is structured for easy AI analysis and extension:

- **Clear Model Relationships**: Well-defined foreign keys and M2M fields
- **Comprehensive Filtering**: Reusable query patterns
- **Template Inheritance**: Consistent structure for UI modifications
- **Admin Integration**: Easy data management interface

## 🎨 UI/UX Features

### Responsive Design
- Mobile-first Bootstrap 5 implementation
- Collapsible navigation and filters
- Card-based layouts for content

### Interactive Elements
- Real-time price range sliders
- Auto-submitting filter forms
- Accordion-style filter sections
- Dynamic result counters

### Accessibility
- Semantic HTML structure
- ARIA labels for form elements
- Keyboard navigation support
- Screen reader friendly

## 🔄 Filter System Deep Dive

### Multi-Select Filtering
```python
# Support for multiple values per filter
institution_categories = self.request.GET.getlist('institution_category')
if institution_categories:
    category_query = Q()
    for category in institution_categories:
        category_query |= Q(institution_category__name__icontains=category)
    queryset = queryset.filter(category_query)
```

### Query Preservation
Templates maintain all GET parameters during pagination and form submission, ensuring user selections persist across page navigation.

### Dynamic Context
Views provide comprehensive context data including:
- All available filter options
- Currently selected filters
- Result counts
- Pagination information

## 🚀 Performance Considerations

### Database Optimization
- `select_related()` and `prefetch_related()` for foreign key relationships
- Indexed fields for common queries
- Distinct() calls to prevent duplicates in M2M queries

### Frontend Optimization
- CDN resources for Bootstrap and Font Awesome
- Compressed assets
- Lazy loading considerations for images

## 🔮 Future Enhancements

### Planned Features
1. **API Endpoints**: REST API for mobile applications
2. **Search Enhancement**: Elasticsearch integration
3. **User Accounts**: Student profiles and favorites
4. **Comparison Tool**: Side-by-side university comparison
5. **Real-time Updates**: WebSocket integration for live data

### Scaling Considerations
- Database migration to PostgreSQL
- Redis caching for filtered queries
- CDN integration for media files
- Load balancing for high traffic

## 📊 Data Management

### Admin Workflow
1. **Universities**: Create with basic information and relationships
2. **Directions**: Add as inline or separately with fee structures
3. **Categories**: Maintain reference data (locations, types, etc.)
4. **Media**: Upload and manage logos, gallery images

### Data Integrity
- Model validation for required relationships
- Slug auto-generation for SEO-friendly URLs
- File cleanup on model deletion

## 🛠️ Development Workflow

### Adding New Features
1. **Models**: Extend existing models or create new ones
2. **Views**: Implement filtering and display logic
3. **Templates**: Create responsive UI components
4. **Admin**: Configure management interfaces
5. **URLs**: Define routing patterns

### Best Practices
- Follow Django conventions
- Use class-based views for consistency
- Implement proper error handling
- Add comprehensive tests
- Document API changes

## 📄 License & Contributing

This project is designed for educational and institutional use. Contributions are welcome through:
- Bug reports and feature requests
- Code improvements and optimizations
- Documentation enhancements
- UI/UX improvements

---

**Note for AI Instances**: This documentation provides a comprehensive overview of the codebase structure, making it easier to understand relationships, extend functionality, and maintain code quality. The project follows Django best practices and modern web development standards. 