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
]