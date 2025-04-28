# urls.py
from django.urls import path
from . import views

# Define an app_name if this is inside a Django app
app_name = 'university_app' # Choose an appropriate name

urlpatterns = [
    path('universities/', views.university_list, name='university_list'),
    path('directions/', views.direction_list, name='direction_list'),
    # Add paths for detail views if you create them
    # path('universities/<slug:slug>/', views.university_detail, name='university_detail'),
    # path('directions/<slug:slug>/', views.direction_detail, name='direction_detail'),

    # Optional: Set a default view (e.g., redirect to universities)
    path('', views.university_list, name='home'), # Or redirect: from django.views.generic import RedirectView
                                                # path('', RedirectView.as_view(pattern_name='university_app:university_list', permanent=False)),
]
