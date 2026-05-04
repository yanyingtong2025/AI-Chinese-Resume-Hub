from django.urls import path
from . import views

urlpatterns = [
    path('',views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    #控制台
    path('hr/dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('jobseeker/dashboard/', views.jobseeker_dashboard, name='jobseeker_dashboard'),
]