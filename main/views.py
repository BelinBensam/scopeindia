from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .models import (
    Course, Syllabus, Placement, FAQ, Contact, AboutContent,
    Country, State, City, Student, Enrollment
)
from .forms import (
    RegistrationForm, LoginForm, ForgotPasswordForm, ContactForm
)
from .services import (
    generate_temporary_password, send_temp_password_email,
    send_password_reset_temp_email, send_contact_email
)


def home(request):
    featured_courses = Course.objects.filter(is_active=True).order_by('name')[:6]
    placements = Placement.objects.all().order_by('-created_at')[:6]
    faqs = FAQ.objects.filter(is_active=True).order_by('order')[:5]
    about_snippet = AboutContent.objects.first()
    context = {
        'featured_courses': featured_courses,
        'placements': placements,
        'faqs': faqs,
        'about_snippet': about_snippet,
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_placements': Placement.objects.count(),
        'total_students': Student.objects.count(),
    }
    return render(request, 'main/home.html', context)


def about(request):
    about_contents = AboutContent.objects.all().order_by('created_at')
    context = {
        'about_contents': about_contents,
    }
    return render(request, 'main/about.html', context)


def courses(request):
    course_list = Course.objects.filter(is_active=True).prefetch_related('syllabus_modules')
    context = {
        'courses': course_list,
    }
    return render(request, 'main/courses.html', context)


def course_detail(request, id):
    course = get_object_or_404(Course, id=id, is_active=True)
    syllabus_list = course.syllabus_modules.all().order_by('order', 'id')
    is_enrolled = False
    if request.user.is_authenticated and hasattr(request.user, 'student_profile'):
        is_enrolled = Enrollment.objects.filter(student=request.user.student_profile, course=course).exists()

    context = {
        'course': course,
        'syllabus_list': syllabus_list,
        'is_enrolled': is_enrolled,
    }
    return render(request, 'main/course_detail.html', context)


def placements(request):
    all_placements = Placement.objects.all().order_by('-created_at')
    context = {
        'placements': all_placements,
    }
    return render(request, 'main/placements.html', context)


def faq(request):
    faqs = FAQ.objects.filter(is_active=True).order_by('order', 'id')
    context = {
        'faqs': faqs,
    }
    return render(request, 'main/faq.html', context)


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_instance = form.save()
            try:
                send_contact_email(contact_instance)
            except Exception:
                pass
            messages.success(request, "Thank you! Your message has been sent successfully. Our team will contact you shortly.")
            return redirect('contact')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request, 'main/contact.html', context)


def register(request):
    # Only redirect active students who already have an account to dashboard
    if request.user.is_authenticated and hasattr(request.user, 'student_profile') and not request.user.is_staff:
        return redirect('dashboard_home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Clear any prior session (e.g. staff session) so newly registered student is not shadowed
                    if request.user.is_authenticated:
                        logout(request)

                    # Generate temporary password
                    temp_pwd = generate_temporary_password(10)
                    email = form.cleaned_data['email']

                    # Create Auth User
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=temp_pwd,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                    )

                    # Create Student Profile
                    # email_verified=True immediately because temp-password receipt proves email ownership
                    student = Student.objects.create(
                        user=user,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                        gender=form.cleaned_data['gender'],
                        date_of_birth=form.cleaned_data['date_of_birth'],
                        phone=form.cleaned_data['phone'],
                        country=form.cleaned_data['country'],
                        state=form.cleaned_data['state'],
                        city=form.cleaned_data['city'],
                        avatar=form.cleaned_data.get('avatar'),
                        email_verified=True,
                        force_password_change=True,
                        temp_password_created_at=timezone.now(),
                    )

                    # Assign ManyToMany Hobbies
                    if form.cleaned_data.get('hobbies'):
                        student.hobbies.set(form.cleaned_data['hobbies'])

                    # Send ONLY the temporary password by email (no verification link)
                    send_temp_password_email(user, student, temp_pwd)

                    request.session['registration_email'] = email
                    request.session['registration_temp_password'] = temp_pwd

                    messages.success(
                        request,
                        "Registration successful! Your temporary login password has been generated. "
                        "Please log in to your student dashboard to set your permanent password."
                    )
                    return redirect('registration_success')

            except Exception as e:
                messages.error(request, f"An unexpected error occurred during registration: {str(e)}")
        else:
            messages.error(request, "Please check the form and fix the highlighted errors.")
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'main/register.html', context)


def registration_success(request):
    registered_email = request.session.get('registration_email', 'your email')
    temp_password = request.session.get('registration_temp_password')
    context = {
        'registered_email': registered_email,
        'temp_password': temp_password,
    }
    return render(request, 'main/registration_success.html', context)


def user_login(request):
    # Only redirect active students who already have an account to dashboard
    if request.user.is_authenticated and hasattr(request.user, 'student_profile') and not request.user.is_staff:
        return redirect('dashboard_home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']

            # Find user by email or username
            try:
                user_obj = User.objects.get(email__iexact=email)
                username = user_obj.username
            except User.DoesNotExist:
                try:
                    user_obj = User.objects.get(username__iexact=email)
                    username = user_obj.username
                except User.DoesNotExist:
                    user_obj = None
                    username = email

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, "This account is inactive. Please contact support.")
                    return render(request, 'main/login.html', {'form': form})

                # Login user
                login(request, user)

                # Remember Me handling
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Browser close

                # Check force_password_change (first login or post-reset)
                if hasattr(user, 'student_profile') and user.student_profile.force_password_change:
                    messages.warning(request, "You are using a temporary password. Please set your new permanent password to continue.")
                    return redirect('change_password')

                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('dashboard_home')
            else:
                messages.error(request, "Invalid email or password. Please try again.")
        else:
            messages.error(request, "Please enter valid login details.")
    else:
        form = LoginForm()

    return render(request, 'main/login.html', {'form': form})


def forgot_password(request):
    """
    Password recovery: generate a new temp password, email it (no reset link),
    and redirect user to login. On login, force_password_change will redirect them
    to change_password view.
    """
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                # Security: don't reveal whether email exists
                messages.success(request, "If that email is registered, a temporary password has been sent. Please check your inbox.")
                return redirect('login')

            sent, temp_pwd = send_password_reset_temp_email(user)

            if sent:
                messages.success(
                    request,
                    f"A temporary password has been sent to {email}. "
                    "Log in with it and you will be prompted to set a new password."
                )
            else:
                messages.error(request, "There was an issue sending the email. Please try again or contact support.")
            return redirect('login')
        else:
            messages.error(request, "Please provide a valid registered email address.")
    else:
        form = ForgotPasswordForm()

    return render(request, 'main/forgot_password.html', {'form': form})


# API Endpoints for Dependent Dropdowns
@require_GET
def api_get_states(request, country_id):
    states = State.objects.filter(country_id=country_id).values('id', 'name').order_by('name')
    return JsonResponse(list(states), safe=False)


@require_GET
def api_get_cities(request, state_id):
    cities = City.objects.filter(state_id=state_id).values('id', 'name').order_by('name')
    return JsonResponse(list(cities), safe=False)
