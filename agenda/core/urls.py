from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, dashboard_view

app_name = 'core'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='core:login'), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
]