from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST

from main.models import Course, Enrollment, Student
from .forms import ProfileForm, ChangePasswordForm


def student_required(view_func):
    """
    Decorator to ensure user is logged in, has a student profile,
    and has satisfied any force_password_change requirement before accessing other pages.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'student_profile'):
            messages.error(request, "Access restricted to student accounts.")
            return redirect('login')

        student = request.user.student_profile
        # Force password change check
        if student.force_password_change and request.resolver_match.url_name != 'change_password' and request.resolver_match.url_name != 'student_logout':
            messages.warning(request, "Please change your temporary password before accessing the dashboard.")
            return redirect('change_password')

        return view_func(request, *args, **kwargs)
    return wrapper


@student_required
def dashboard_home(request):
    student = request.user.student_profile
    my_enrollments = Enrollment.objects.filter(student=student).select_related('course').order_by('-enrolled_at')
    enrolled_course_ids = my_enrollments.values_list('course_id', flat=True)

    available_courses = Course.objects.filter(is_active=True).exclude(id__in=enrolled_course_ids)[:4]

    context = {
        'student': student,
        'total_enrolled': my_enrollments.count(),
        'available_courses_count': Course.objects.filter(is_active=True).count(),
        'recent_enrollments': my_enrollments[:5],
        'recommended_courses': available_courses,
    }
    return render(request, 'dashboard/dashboard.html', context)


@student_required
def courses_catalog(request):
    student = request.user.student_profile
    query = request.GET.get('q', '').strip()

    courses_qs = Course.objects.filter(is_active=True).prefetch_related('syllabus_modules')
    if query:
        courses_qs = courses_qs.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    enrolled_course_ids = Enrollment.objects.filter(student=student).values_list('course_id', flat=True)

    context = {
        'student': student,
        'courses': courses_qs,
        'query': query,
        'enrolled_course_ids': set(enrolled_course_ids),
    }
    return render(request, 'dashboard/courses.html', context)


@student_required
@require_POST
def course_enroll(request, course_id):
    student = request.user.student_profile
    course = get_object_or_404(Course, id=course_id, is_active=True)

    # Check duplicate enrollment
    enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
    if created:
        messages.success(request, f"Successfully signed up for '{course.name}'!")
    else:
        messages.info(request, f"You have already signed up for '{course.name}'.")

    # Redirect back to referring page or my courses
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'dashboard_courses'
    return redirect(next_url)


@student_required
def my_courses(request):
    student = request.user.student_profile
    enrollments = Enrollment.objects.filter(student=student).select_related('course').order_by('-enrolled_at')

    context = {
        'student': student,
        'enrollments': enrollments,
    }
    return render(request, 'dashboard/my_courses.html', context)


@student_required
def profile_view(request):
    student = request.user.student_profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            updated_student = form.save()

            # Keep User model's first_name and last_name synchronized
            user = request.user
            user.first_name = updated_student.first_name
            user.last_name = updated_student.last_name
            user.save()

            messages.success(request, "Your profile has been updated successfully.")
            return redirect('student_profile')
        else:
            messages.error(request, "Please correct the errors in the profile form.")
    else:
        form = ProfileForm(instance=student)

    context = {
        'student': student,
        'form': form,
    }
    return render(request, 'dashboard/profile.html', context)


@login_required
def change_password_view(request):
    user = request.user
    student = getattr(user, 'student_profile', None)

    if request.method == 'POST':
        form = ChangePasswordForm(user=user, data=request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()

            if student:
                student.force_password_change = False
                student.save()

            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been successfully set! Welcome to your student dashboard.")
            return redirect('dashboard_home')
        else:
            messages.error(request, "Please fix the password errors below.")
    else:
        form = ChangePasswordForm(user=user)

    context = {
        'form': form,
        'student': student,
        'is_forced': student.force_password_change if student else False,
    }
    return render(request, 'dashboard/change_password.html', context)


@login_required
def student_logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')
