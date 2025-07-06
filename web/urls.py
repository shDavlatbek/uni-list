from django.urls import path
from . import views

app_name = 'universities'

urlpatterns = [
    # Home page
    path('', views.home_view, name='home'),
    
    # University list with filters
    path('universities/', views.UniversityListView.as_view(), name='university_list'),
    
    # Direction list with filters
    path('directions/', views.DirectionListView.as_view(), name='direction_list'),
    
    # University detail view
    path('universities/<slug:slug>/', views.UniversityDetailView.as_view(), name='university_detail'),
    
    # Direction detail view
    path('directions/<slug:direction_slug>/', views.DirectionDetailView.as_view(), name='direction_detail'),
    
    # API Endpoints for Dynamic Filtering
    path('api/universities/filter/', views.university_filter_api, name='university_filter_api'),
    path('api/directions/filter/', views.direction_filter_api, name='direction_filter_api'),
    path('api/filter-options/', views.filter_options_api, name='filter_options_api'),
]