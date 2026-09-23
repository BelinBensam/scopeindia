from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('courses/', views.courses_catalog, name='dashboard_courses'),
    path('courses/<int:course_id>/enroll/', views.course_enroll, name='dashboard_course_enroll'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('profile/', views.profile_view, name='student_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('logout/', views.student_logout_view, name='student_logout'),
]
