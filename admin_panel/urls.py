from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_panel_index'),
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Courses CRUD
    path('courses/', views.course_list, name='admin_course_list'),
    path('courses/add/', views.course_create, name='admin_course_create'),
    path('courses/<int:id>/edit/', views.course_edit, name='admin_course_edit'),
    path('courses/<int:id>/delete/', views.course_delete, name='admin_course_delete'),

    # Syllabus CRUD
    path('syllabus/', views.syllabus_list, name='admin_syllabus_list'),
    path('syllabus/add/', views.syllabus_create, name='admin_syllabus_create'),
    path('syllabus/<int:id>/edit/', views.syllabus_edit, name='admin_syllabus_edit'),
    path('syllabus/<int:id>/delete/', views.syllabus_delete, name='admin_syllabus_delete'),

    # Placements CRUD
    path('placements/', views.placement_list, name='admin_placement_list'),
    path('placements/add/', views.placement_create, name='admin_placement_create'),
    path('placements/<int:id>/edit/', views.placement_edit, name='admin_placement_edit'),
    path('placements/<int:id>/delete/', views.placement_delete, name='admin_placement_delete'),

    # FAQ CRUD
    path('faq/', views.faq_list, name='admin_faq_list'),
    path('faq/add/', views.faq_create, name='admin_faq_create'),
    path('faq/<int:id>/edit/', views.faq_edit, name='admin_faq_edit'),
    path('faq/<int:id>/delete/', views.faq_delete, name='admin_faq_delete'),

    # Students Management
    path('students/', views.student_list, name='admin_student_list'),
    path('students/<int:id>/', views.student_detail, name='admin_student_detail'),

    # Enrollments Management
    path('enrollments/', views.enrollment_list, name='admin_enrollment_list'),
    path('enrollments/<int:id>/delete/', views.enrollment_delete, name='admin_enrollment_delete'),

    # Contacts Management
    path('contacts/', views.contact_list, name='admin_contact_list'),
    path('contacts/<int:id>/toggle/', views.contact_toggle_read, name='admin_contact_toggle_read'),
    path('contacts/<int:id>/delete/', views.contact_delete, name='admin_contact_delete'),

    # Locations: Countries, States, Cities
    path('countries/', views.country_list, name='admin_country_list'),
    path('countries/<int:id>/edit/', views.country_edit, name='admin_country_edit'),
    path('countries/<int:id>/delete/', views.country_delete, name='admin_country_delete'),

    path('states/', views.state_list, name='admin_state_list'),
    path('states/<int:id>/edit/', views.state_edit, name='admin_state_edit'),
    path('states/<int:id>/delete/', views.state_delete, name='admin_state_delete'),

    path('cities/', views.city_list, name='admin_city_list'),
    path('cities/<int:id>/edit/', views.city_edit, name='admin_city_edit'),
    path('cities/<int:id>/delete/', views.city_delete, name='admin_city_delete'),

    # Hobbies CRUD
    path('hobbies/', views.hobby_list, name='admin_hobby_list'),
    path('hobbies/<int:id>/edit/', views.hobby_edit, name='admin_hobby_edit'),
    path('hobbies/<int:id>/delete/', views.hobby_delete, name='admin_hobby_delete'),

    # About Content CRUD
    path('about/', views.about_list, name='admin_about_list'),
    path('about/add/', views.about_create, name='admin_about_create'),
    path('about/<int:id>/edit/', views.about_edit, name='admin_about_edit'),
    path('about/<int:id>/delete/', views.about_delete, name='admin_about_delete'),
]
