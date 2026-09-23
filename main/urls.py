from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('courses/', views.courses, name='courses'),
    path('courses/<int:id>/', views.course_detail, name='course_detail'),
    path('placements/', views.placements, name='placements'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('login/', views.user_login, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # Location APIs for dynamic dropdowns
    path('api/states/<int:country_id>/', views.api_get_states, name='api_states'),
    path('api/cities/<int:state_id>/', views.api_get_cities, name='api_cities'),
]
