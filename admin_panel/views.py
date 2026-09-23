from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

from main.models import (
    Student, Course, Syllabus, Placement, FAQ, Contact,
    Enrollment, Country, State, City, Hobby, AboutContent
)
from .forms import (
    AdminLoginForm, CourseForm, SyllabusForm, PlacementForm, FAQForm,
    CountryForm, StateForm, CityForm, HobbyForm, AboutContentForm
)


def admin_required(view_func):
    """
    Ensure user is authenticated and has staff status.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not request.user.is_staff:
            messages.error(request, "Access denied. Administrator credentials required.")
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, f"Welcome to SCOPE INDIA Admin Panel, {form.user.username}!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid administrator credentials.")
    else:
        form = AdminLoginForm()

    return render(request, 'admin_panel/login.html', {'form': form})


def admin_logout_view(request):
    logout(request)
    messages.info(request, "Admin logged out successfully.")
    return redirect('admin_login')


@admin_required
def admin_dashboard(request):
    context = {
        'total_students': Student.objects.count(),
        'total_courses': Course.objects.count(),
        'total_placements': Placement.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'total_faqs': FAQ.objects.count(),
        'total_contacts': Contact.objects.count(),
        'unread_contacts': Contact.objects.filter(is_read=False).count(),
        'recent_students': Student.objects.select_related('user', 'country', 'city').order_by('-created_at')[:5],
        'recent_enrollments': Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')[:5],
        'recent_contacts': Contact.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ==========================================
# COURSE CRUD
# ==========================================
@admin_required
def course_list(request):
    q = request.GET.get('q', '').strip()
    courses = Course.objects.all().prefetch_related('syllabus_modules').order_by('-id')
    if q:
        courses = courses.filter(Q(name__icontains=q) | Q(description__icontains=q))

    paginator = Paginator(courses, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/courses/list.html', {'page_obj': page_obj, 'q': q})


@admin_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save()
            messages.success(request, f"Course '{course.name}' created successfully!")
            return redirect('admin_course_list')
    else:
        form = CourseForm()
    return render(request, 'admin_panel/courses/form.html', {'form': form, 'title': 'Add New Course'})


@admin_required
def course_edit(request, id):
    course = get_object_or_404(Course, id=id)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.name}' updated successfully!")
            return redirect('admin_course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'admin_panel/courses/form.html', {'form': form, 'course': course, 'title': f'Edit Course: {course.name}'})


@admin_required
@require_POST
def course_delete(request, id):
    course = get_object_or_404(Course, id=id)
    course_name = course.name
    course.delete()
    messages.success(request, f"Course '{course_name}' has been deleted.")
    return redirect('admin_course_list')


# ==========================================
# SYLLABUS CRUD
# ==========================================
@admin_required
def syllabus_list(request):
    course_id = request.GET.get('course_id')
    syllabi = Syllabus.objects.select_related('course').order_by('course__name', 'order', 'id')
    courses = Course.objects.all().order_by('name')

    if course_id:
        syllabi = syllabi.filter(course_id=course_id)

    paginator = Paginator(syllabi, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/syllabus/list.html', {
        'page_obj': page_obj,
        'courses': courses,
        'selected_course_id': course_id
    })


@admin_required
def syllabus_create(request):
    initial_course_id = request.GET.get('course_id')
    if request.method == 'POST':
        form = SyllabusForm(request.POST)
        if form.is_valid():
            s = form.save()
            messages.success(request, f"Syllabus module '{s.title}' added to {s.course.name}!")
            return redirect('admin_syllabus_list')
    else:
        form = SyllabusForm(initial={'course': initial_course_id} if initial_course_id else None)
    return render(request, 'admin_panel/syllabus/form.html', {'form': form, 'title': 'Add Syllabus Module'})


@admin_required
def syllabus_edit(request, id):
    syllabus = get_object_or_404(Syllabus, id=id)
    if request.method == 'POST':
        form = SyllabusForm(request.POST, instance=syllabus)
        if form.is_valid():
            form.save()
            messages.success(request, "Syllabus module updated.")
            return redirect('admin_syllabus_list')
    else:
        form = SyllabusForm(instance=syllabus)
    return render(request, 'admin_panel/syllabus/form.html', {'form': form, 'title': 'Edit Syllabus Module'})


@admin_required
@require_POST
def syllabus_delete(request, id):
    syllabus = get_object_or_404(Syllabus, id=id)
    syllabus.delete()
    messages.success(request, "Syllabus module deleted.")
    return redirect('admin_syllabus_list')


# ==========================================
# PLACEMENT CRUD
# ==========================================
@admin_required
def placement_list(request):
    placements = Placement.objects.all().order_by('-created_at')
    paginator = Paginator(placements, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/placements/list.html', {'page_obj': page_obj})


@admin_required
def placement_create(request):
    if request.method == 'POST':
        form = PlacementForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save()
            messages.success(request, f"Placement record for '{p.name}' created!")
            return redirect('admin_placement_list')
    else:
        form = PlacementForm()
    return render(request, 'admin_panel/placements/form.html', {'form': form, 'title': 'Add Placement Record'})


@admin_required
def placement_edit(request, id):
    placement = get_object_or_404(Placement, id=id)
    if request.method == 'POST':
        form = PlacementForm(request.POST, request.FILES, instance=placement)
        if form.is_valid():
            form.save()
            messages.success(request, "Placement record updated.")
            return redirect('admin_placement_list')
    else:
        form = PlacementForm(instance=placement)
    return render(request, 'admin_panel/placements/form.html', {'form': form, 'title': 'Edit Placement Record'})


@admin_required
@require_POST
def placement_delete(request, id):
    placement = get_object_or_404(Placement, id=id)
    placement.delete()
    messages.success(request, "Placement record removed.")
    return redirect('admin_placement_list')


# ==========================================
# FAQ CRUD
# ==========================================
@admin_required
def faq_list(request):
    faqs = FAQ.objects.all().order_by('order', 'id')
    return render(request, 'admin_panel/faq/list.html', {'faqs': faqs})


@admin_required
def faq_create(request):
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ item created!")
            return redirect('admin_faq_list')
    else:
        form = FAQForm()
    return render(request, 'admin_panel/faq/form.html', {'form': form, 'title': 'Add FAQ Item'})


@admin_required
def faq_edit(request, id):
    faq_item = get_object_or_404(FAQ, id=id)
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq_item)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ item updated.")
            return redirect('admin_faq_list')
    else:
        form = FAQForm(instance=faq_item)
    return render(request, 'admin_panel/faq/form.html', {'form': form, 'title': 'Edit FAQ Item'})


@admin_required
@require_POST
def faq_delete(request, id):
    faq_item = get_object_or_404(FAQ, id=id)
    faq_item.delete()
    messages.success(request, "FAQ item deleted.")
    return redirect('admin_faq_list')


# ==========================================
# STUDENT MANAGEMENT
# ==========================================
@admin_required
def student_list(request):
    q = request.GET.get('q', '').strip()
    verified_filter = request.GET.get('verified')

    students = Student.objects.select_related('user', 'country', 'state', 'city').prefetch_related('hobbies', 'enrollments__course').order_by('-created_at')

    if q:
        students = students.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(user__email__icontains=q) |
            Q(phone__icontains=q)
        )
    if verified_filter == 'yes':
        students = students.filter(email_verified=True)
    elif verified_filter == 'no':
        students = students.filter(email_verified=False)

    paginator = Paginator(students, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/students/list.html', {
        'page_obj': page_obj,
        'q': q,
        'verified_filter': verified_filter
    })


@admin_required
def student_detail(request, id):
    student = get_object_or_404(
        Student.objects.select_related('user', 'country', 'state', 'city').prefetch_related('hobbies', 'enrollments__course'),
        id=id
    )
    return render(request, 'admin_panel/students/detail.html', {'student': student})


# ==========================================
# ENROLLMENT MANAGEMENT
# ==========================================
@admin_required
def enrollment_list(request):
    q = request.GET.get('q', '').strip()
    enrollments = Enrollment.objects.select_related('student__user', 'course').order_by('-enrolled_at')

    if q:
        enrollments = enrollments.filter(
            Q(student__first_name__icontains=q) |
            Q(student__last_name__icontains=q) |
            Q(student__user__email__icontains=q) |
            Q(course__name__icontains=q)
        )

    paginator = Paginator(enrollments, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/enrollments/list.html', {'page_obj': page_obj, 'q': q})


@admin_required
@require_POST
def enrollment_delete(request, id):
    enrollment = get_object_or_404(Enrollment, id=id)
    enrollment.delete()
    messages.success(request, "Enrollment cancelled.")
    return redirect('admin_enrollment_list')


# ==========================================
# CONTACT MESSAGES
# ==========================================
@admin_required
def contact_list(request):
    contacts = Contact.objects.all().order_by('-created_at')
    paginator = Paginator(contacts, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/contacts/list.html', {'page_obj': page_obj})


@admin_required
@require_POST
def contact_toggle_read(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.is_read = not contact.is_read
    contact.save()
    messages.success(request, f"Marked message from {contact.name} as {'read' if contact.is_read else 'unread'}.")
    return redirect('admin_contact_list')


@admin_required
@require_POST
def contact_delete(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    messages.success(request, "Contact message deleted.")
    return redirect('admin_contact_list')


# ==========================================
# LOCATION MANAGEMENT: COUNTRIES, STATES, CITIES
# ==========================================
@admin_required
def country_list(request):
    countries = Country.objects.prefetch_related('states').all().order_by('name')
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Country added successfully.")
            return redirect('admin_country_list')
    else:
        form = CountryForm()
    return render(request, 'admin_panel/countries/list.html', {'countries': countries, 'form': form})


@admin_required
def country_edit(request, id):
    country = get_object_or_404(Country, id=id)
    if request.method == 'POST':
        form = CountryForm(request.POST, instance=country)
        if form.is_valid():
            form.save()
            messages.success(request, "Country updated.")
            return redirect('admin_country_list')
    else:
        form = CountryForm(instance=country)
    return render(request, 'admin_panel/countries/form.html', {'form': form, 'title': f'Edit Country: {country.name}'})


@admin_required
@require_POST
def country_delete(request, id):
    country = get_object_or_404(Country, id=id)
    country.delete()
    messages.success(request, "Country deleted.")
    return redirect('admin_country_list')


@admin_required
def state_list(request):
    country_id = request.GET.get('country')
    states = State.objects.select_related('country').all().order_by('country__name', 'name')
    countries = Country.objects.all().order_by('name')

    if country_id:
        states = states.filter(country_id=country_id)

    if request.method == 'POST':
        form = StateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "State added successfully.")
            return redirect('admin_state_list')
    else:
        form = StateForm(initial={'country': country_id} if country_id else None)

    paginator = Paginator(states, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/states/list.html', {
        'page_obj': page_obj,
        'countries': countries,
        'selected_country': country_id,
        'form': form
    })


@admin_required
def state_edit(request, id):
    state = get_object_or_404(State, id=id)
    if request.method == 'POST':
        form = StateForm(request.POST, instance=state)
        if form.is_valid():
            form.save()
            messages.success(request, "State updated.")
            return redirect('admin_state_list')
    else:
        form = StateForm(instance=state)
    return render(request, 'admin_panel/states/form.html', {'form': form, 'title': f'Edit State: {state.name}'})


@admin_required
@require_POST
def state_delete(request, id):
    state = get_object_or_404(State, id=id)
    state.delete()
    messages.success(request, "State deleted.")
    return redirect('admin_state_list')


@admin_required
def city_list(request):
    state_id = request.GET.get('state')
    cities = City.objects.select_related('state__country').all().order_by('state__name', 'name')
    states = State.objects.select_related('country').all().order_by('name')

    if state_id:
        cities = cities.filter(state_id=state_id)

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "City added successfully.")
            return redirect('admin_city_list')
    else:
        form = CityForm(initial={'state': state_id} if state_id else None)

    paginator = Paginator(cities, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/cities/list.html', {
        'page_obj': page_obj,
        'states': states,
        'selected_state': state_id,
        'form': form
    })


@admin_required
def city_edit(request, id):
    city = get_object_or_404(City, id=id)
    if request.method == 'POST':
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            messages.success(request, "City updated.")
            return redirect('admin_city_list')
    else:
        form = CityForm(instance=city)
    return render(request, 'admin_panel/cities/form.html', {'form': form, 'title': f'Edit City: {city.name}'})


@admin_required
@require_POST
def city_delete(request, id):
    city = get_object_or_404(City, id=id)
    city.delete()
    messages.success(request, "City deleted.")
    return redirect('admin_city_list')


# ==========================================
# HOBBIES CRUD
# ==========================================
@admin_required
def hobby_list(request):
    hobbies = Hobby.objects.all().order_by('name')
    if request.method == 'POST':
        form = HobbyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Hobby added successfully.")
            return redirect('admin_hobby_list')
    else:
        form = HobbyForm()
    return render(request, 'admin_panel/hobbies/list.html', {'hobbies': hobbies, 'form': form})


@admin_required
def hobby_edit(request, id):
    hobby = get_object_or_404(Hobby, id=id)
    if request.method == 'POST':
        form = HobbyForm(request.POST, instance=hobby)
        if form.is_valid():
            form.save()
            messages.success(request, "Hobby updated.")
            return redirect('admin_hobby_list')
    else:
        form = HobbyForm(instance=hobby)
    return render(request, 'admin_panel/hobbies/form.html', {'form': form, 'title': f'Edit Hobby: {hobby.name}'})


@admin_required
@require_POST
def hobby_delete(request, id):
    hobby = get_object_or_404(Hobby, id=id)
    hobby.delete()
    messages.success(request, "Hobby deleted.")
    return redirect('admin_hobby_list')


# ==========================================
# ABOUT CONTENT CRUD
# ==========================================
@admin_required
def about_list(request):
    about_contents = AboutContent.objects.all().order_by('created_at')
    return render(request, 'admin_panel/about/list.html', {'about_contents': about_contents})


@admin_required
def about_create(request):
    if request.method == 'POST':
        form = AboutContentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "About section added.")
            return redirect('admin_about_list')
    else:
        form = AboutContentForm()
    return render(request, 'admin_panel/about/form.html', {'form': form, 'title': 'Add About Section'})


@admin_required
def about_edit(request, id):
    about_item = get_object_or_404(AboutContent, id=id)
    if request.method == 'POST':
        form = AboutContentForm(request.POST, request.FILES, instance=about_item)
        if form.is_valid():
            form.save()
            messages.success(request, "About section updated.")
            return redirect('admin_about_list')
    else:
        form = AboutContentForm(instance=about_item)
    return render(request, 'admin_panel/about/form.html', {'form': form, 'title': f'Edit About: {about_item.title}'})


@admin_required
@require_POST
def about_delete(request, id):
    about_item = get_object_or_404(AboutContent, id=id)
    about_item.delete()
    messages.success(request, "About section deleted.")
    return redirect('admin_about_list')
