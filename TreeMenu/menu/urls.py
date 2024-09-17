from django.urls import path
from .views import home_view, menu_view

urlpatterns = [
    path('', home_view, name='home'),
    path('<path:menu>/', menu_view, name='menu'),
]