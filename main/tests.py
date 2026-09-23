from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import (
    Country, State, City, Hobby, Course, Syllabus, Placement,
    FAQ, Contact, Student, Enrollment
)
from .forms import RegistrationForm


class ScopeIndiaAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Seed basic location data
        self.india = Country.objects.create(name="India")
        self.usa = Country.objects.create(name="United States")
        self.kerala = State.objects.create(country=self.india, name="Kerala")
        self.tamil_nadu = State.objects.create(country=self.india, name="Tamil Nadu")
        self.california = State.objects.create(country=self.usa, name="California")

        self.tvm = City.objects.create(state=self.kerala, name="Thiruvananthapuram")
        self.kochi = City.objects.create(state=self.kerala, name="Kochi")
        self.chennai = City.objects.create(state=self.tamil_nadu, name="Chennai")

        # Hobby
        self.hobby1 = Hobby.objects.create(name="Python Programming")
        self.hobby2 = Hobby.objects.create(name="Web Development")

        # Course & Syllabus
        self.course = Course.objects.create(
            name="Python Full Stack Development",
            duration="6 Months",
            fee=38000.00,
            description="Complete full stack training course.",
            is_active=True
        )
        self.syllabus1 = Syllabus.objects.create(
            course=self.course,
            title="Module 1: Python Basics",
            description="Core syntax and data structures.",
            order=1
        )

        # Admin user
        self.admin_user = User.objects.create_user(
            username="admin@scopeindia.org",
            email="admin@scopeindia.org",
            password="Admin@Password123",
            is_staff=True,
            is_superuser=True
        )

        # Student user
        self.student_user = User.objects.create_user(
            username="student@example.com",
            email="student@example.com",
            password="Student@Password123",
            first_name="John",
            last_name="Doe"
        )
        self.student_profile = Student.objects.create(
            user=self.student_user,
            first_name="John",
            last_name="Doe",
            gender="Male",
            date_of_birth=date(2000, 1, 1),
            phone="9876543210",
            country=self.india,
            state=self.kerala,
            city=self.tvm,
            email_verified=True,
            force_password_change=False
        )

    # 1. PUBLIC PAGES TESTS
    def test_public_pages_load(self):
        urls = [
            reverse('home'),
            reverse('about'),
            reverse('courses'),
            reverse('course_detail', kwargs={'id': self.course.id}),
            reverse('placements'),
            reverse('faq'),
            reverse('contact'),
            reverse('register'),
            reverse('login'),
            reverse('forgot_password'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, f"Failed to load {url}")

    # 2. DYNAMIC LOCATION API TESTS
    def test_api_get_states(self):
        url = reverse('api_states', kwargs={'country_id': self.india.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        state_names = [s['name'] for s in data]
        self.assertIn("Kerala", state_names)
        self.assertIn("Tamil Nadu", state_names)
        self.assertNotIn("California", state_names)

    def test_api_get_cities(self):
        url = reverse('api_cities', kwargs={'state_id': self.kerala.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        city_names = [c['name'] for c in data]
        self.assertIn("Thiruvananthapuram", city_names)
        self.assertNotIn("Chennai", city_names)

    # 3. REGISTRATION VALIDATION TESTS
    def test_registration_country_state_mismatch_validation(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'Male',
            'date_of_birth': '2000-01-01',
            'email': 'newstudent@example.com',
            'phone': '9876543211',
            'country': self.usa.id,
            'state': self.kerala.id,  # Mismatch: Kerala belongs to India, not USA
            'city': self.tvm.id,
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('state', form.errors)

    def test_registration_state_city_mismatch_validation(self):
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'gender': 'Male',
            'date_of_birth': '2000-01-01',
            'email': 'newstudent@example.com',
            'phone': '9876543211',
            'country': self.india.id,
            'state': self.kerala.id,
            'city': self.chennai.id,  # Mismatch: Chennai belongs to Tamil Nadu, not Kerala
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('city', form.errors)

    def test_registration_duplicate_email(self):
        form_data = {
            'first_name': 'Duplicate',
            'last_name': 'Email',
            'gender': 'Female',
            'date_of_birth': '2001-02-02',
            'email': 'student@example.com',  # Already exists
            'phone': '9876543212',
            'country': self.india.id,
            'state': self.kerala.id,
            'city': self.tvm.id,
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # 4. TEMP PASSWORD LOGIN FLOW
    def test_student_with_verified_email_can_login(self):
        """
        In the new flow, email_verified=True is set immediately at registration.
        A student with verified email and correct password should log in.
        """
        self.student_profile.email_verified = True
        self.student_profile.force_password_change = False
        self.student_profile.save()

        response = self.client.post(reverse('login'), {
            'email': 'student@example.com',
            'password': 'Student@Password123',
        })
        # Should redirect to dashboard (302)
        self.assertEqual(response.status_code, 302)

    def test_student_wrong_password_cannot_login(self):
        """
        A student with the wrong password should be shown an error on the login page.
        """
        self.student_profile.email_verified = True
        self.student_profile.force_password_change = False
        self.student_profile.save()

        response = self.client.post(reverse('login'), {
            'email': 'student@example.com',
            'password': 'WrongPassword!',
        })
        # Should stay on login page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")

    def test_force_password_change_interception(self):
        # Set force_password_change = True
        self.student_profile.force_password_change = True
        self.student_profile.save()

        self.client.login(username='student@example.com', password='Student@Password123')
        # Accessing dashboard should redirect to change_password
        response = self.client.get(reverse('dashboard_home'))
        self.assertRedirects(response, reverse('change_password'))

    # 5. COURSE ENROLLMENT & DUPLICATE PREVENTION
    def test_course_enrollment_and_duplicate_prevention(self):
        self.client.login(username='student@example.com', password='Student@Password123')

        # First enrollment
        response = self.client.post(reverse('dashboard_course_enroll', kwargs={'course_id': self.course.id}))
        self.assertEqual(Enrollment.objects.filter(student=self.student_profile, course=self.course).count(), 1)

        # Duplicate enrollment attempt
        response2 = self.client.post(reverse('dashboard_course_enroll', kwargs={'course_id': self.course.id}))
        # Still 1, no duplicate
        self.assertEqual(Enrollment.objects.filter(student=self.student_profile, course=self.course).count(), 1)

    # 6. COURSE SEARCH TEST
    def test_course_search_q_objects(self):
        self.client.login(username='student@example.com', password='Student@Password123')
        response = self.client.get(reverse('dashboard_courses') + '?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Full Stack Development")

        # Non-matching query
        response2 = self.client.get(reverse('dashboard_courses') + '?q=NonExistentSubject123')
        self.assertEqual(response2.status_code, 200)
        self.assertNotContains(response2, "Python Full Stack Development")

    # 7. ADMIN ACCESS PROTECTION & CRUD
    def test_admin_access_restricted_to_staff(self):
        # Unauthenticated access redirects to admin login
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('admin_login'))

        # Normal student logged in trying to access admin
        self.client.login(username='student@example.com', password='Student@Password123')
        response_student = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response_student, reverse('admin_login'))

    def test_admin_can_access_dashboard_and_create_course(self):
        self.client.login(username='admin@scopeindia.org', password='Admin@Password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Administrative Overview")

        # Create Course via Admin
        response_create = self.client.post(reverse('admin_course_create'), {
            'name': 'DevOps and AWS Engineering',
            'duration': '4 Months',
            'fee': '35000.00',
            'description': 'DevOps industrial curriculum.',
            'is_active': True,
        })
        self.assertRedirects(response_create, reverse('admin_course_list'))
        self.assertTrue(Course.objects.filter(name='DevOps and AWS Engineering').exists())

        # Verify new course shows up automatically on the public website!
        public_resp = self.client.get(reverse('courses'))
        self.assertContains(public_resp, 'DevOps and AWS Engineering')

    def test_admin_delete_requires_post(self):
        self.client.login(username='admin@scopeindia.org', password='Admin@Password123')
        test_course = Course.objects.create(
            name="Temporary Course",
            duration="1 Month",
            fee=5000.00,
            description="Testing delete",
            is_active=True
        )
        # GET request to delete endpoint should fail (405 Method Not Allowed)
        response_get = self.client.get(reverse('admin_course_delete', kwargs={'id': test_course.id}))
        self.assertEqual(response_get.status_code, 405)

        # POST request should succeed
        response_post = self.client.post(reverse('admin_course_delete', kwargs={'id': test_course.id}))
        self.assertRedirects(response_post, reverse('admin_course_list'))
        self.assertFalse(Course.objects.filter(id=test_course.id).exists())
