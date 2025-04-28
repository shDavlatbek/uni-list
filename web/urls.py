# urls.py
from django.urls import path
from . import views

# Define an app_name if this is inside a Django app
app_name = 'university_app' # Choose an appropriate name

urlpatterns = [
    # List Views
    path('universities/', views.university_list, name='university_list'),
    path('directions/', views.direction_list, name='direction_list'),

    # Detail Views (Using slugs)
    path('universities/<slug:slug>/', views.university_detail, name='university_detail'),
    path('directions/<slug:slug>/', views.direction_detail, name='direction_detail'), # Use direction_slug defined in model

    # Optional: Set a default view
    path('', views.university_list, name='home'),
]
