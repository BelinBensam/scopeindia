from django.contrib import admin
from .models import (
    Country, State, City, Hobby, Student, Course, Syllabus,
    Enrollment, Placement, FAQ, Contact, AboutContent
)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state__country', 'state')
    search_fields = ('name', 'state__name')


@admin.register(Hobby)
class HobbyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'get_email', 'phone', 'gender', 'city', 'email_verified', 'created_at')
    list_filter = ('email_verified', 'force_password_change', 'gender', 'country')
    search_fields = ('first_name', 'last_name', 'user__email', 'phone')
    inlines = [EnrollmentInline]

    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email


class SyllabusInline(admin.TabularInline):
    model = Syllabus
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'fee', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    inlines = [SyllabusInline]


@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('course', 'order', 'title')
    list_filter = ('course',)
    search_fields = ('title', 'course__name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__first_name', 'student__last_name', 'course__name')


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'role', 'created_at')
    search_fields = ('name', 'company', 'role')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('question', 'answer')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(AboutContent)
class AboutContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
