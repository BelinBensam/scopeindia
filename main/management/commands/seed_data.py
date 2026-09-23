from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import (
    Country, State, City, Hobby, Course, Syllabus, Placement,
    FAQ, AboutContent, Student, Enrollment
)


class Command(BaseCommand):
    help = "Seeds initial database records for SCOPE INDIA application (SQLite3)"

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        # 1. Countries
        countries_data = ["India", "United States", "United Kingdom", "United Arab Emirates", "Germany"]
        country_objs = {}
        for cname in countries_data:
            c, _ = Country.objects.get_or_create(name=cname)
            country_objs[cname] = c
        self.stdout.write(self.style.SUCCESS(f"Populated {len(country_objs)} countries."))

        # 2. States
        india = country_objs["India"]
        us = country_objs["United States"]

        states_data = [
            (india, "Kerala"),
            (india, "Tamil Nadu"),
            (india, "Karnataka"),
            (india, "Maharashtra"),
            (us, "California"),
            (us, "Texas"),
            (us, "New York"),
        ]
        state_objs = {}
        for c_obj, sname in states_data:
            s, _ = State.objects.get_or_create(country=c_obj, name=sname)
            state_objs[sname] = s
        self.stdout.write(self.style.SUCCESS(f"Populated {len(state_objs)} states."))

        # 3. Cities
        cities_data = [
            (state_objs["Kerala"], "Thiruvananthapuram"),
            (state_objs["Kerala"], "Kochi"),
            (state_objs["Kerala"], "Kozhikode"),
            (state_objs["Kerala"], "Kollam"),
            (state_objs["Tamil Nadu"], "Chennai"),
            (state_objs["Tamil Nadu"], "Coimbatore"),
            (state_objs["Tamil Nadu"], "Nagercoil"),
            (state_objs["Tamil Nadu"], "Madurai"),
            (state_objs["Karnataka"], "Bengaluru"),
            (state_objs["Karnataka"], "Mysuru"),
            (state_objs["Maharashtra"], "Mumbai"),
            (state_objs["Maharashtra"], "Pune"),
            (state_objs["California"], "San Francisco"),
            (state_objs["California"], "Los Angeles"),
        ]
        city_objs = {}
        for s_obj, cname in cities_data:
            city, _ = City.objects.get_or_create(state=s_obj, name=cname)
            city_objs[cname] = city
        self.stdout.write(self.style.SUCCESS(f"Populated {len(city_objs)} cities."))

        # 4. Hobbies / Interests
        hobbies_data = [
            "Python Programming",
            "Web Development",
            "Artificial Intelligence",
            "Cloud & DevOps",
            "Networking & Cybersecurity",
            "Data Science",
            "Mobile App Development"
        ]
        hobby_objs = []
        for h in hobbies_data:
            obj, _ = Hobby.objects.get_or_create(name=h)
            hobby_objs.append(obj)
        self.stdout.write(self.style.SUCCESS(f"Populated {len(hobby_objs)} hobbies."))

        # 5. Courses & Syllabuses
        courses_catalog = [
            {
                "name": "Python Full Stack Development",
                "duration": "6 Months",
                "fee": 38000.00,
                "description": "Comprehensive career track covering Python fundamentals, OOP, Django framework, SQLite3, RESTful APIs, Bootstrap 5, and frontend web development with real-world project deployments.",
                "modules": [
                    ("Python Programming Essentials", "Core syntax, data types, collections, control flows, and file I/O operations.", 1),
                    ("Object Oriented Programming & Design", "Classes, inheritance, polymorphism, encapsulation, and modular design patterns.", 2),
                    ("Frontend Engineering (HTML5/CSS3/JS/Bootstrap)", "Modern responsive layout design, Flexbox, Grid, DOM manipulation, and Bootstrap 5 components.", 3),
                    ("Django Web Framework & MVT Architecture", "Django project structure, views, URLs, models, migrations, forms, and template rendering engine.", 4),
                    ("Database Engineering with SQLite3 & ORM", "Relational database modeling, query optimizations, prefetch, select_related, and indexing.", 5),
                    ("REST API & Fetch API Integration", "Asynchronous HTTP requests, dynamic AJAX data loading, JSON formatting, and API endpoints.", 6),
                    ("Capstone Industrial Project & Deployment", "End-to-end full stack web application development with authentication and production readiness.", 7),
                ]
            },
            {
                "name": "Java Full Stack & Microservices",
                "duration": "6 Months",
                "fee": 40000.00,
                "description": "Enterprise software development program focusing on Core Java, Spring Boot, Microservices, Hibernate, REST APIs, and modern frontend frameworks with 100% placement assurance.",
                "modules": [
                    ("Core Java & Advanced OOP", "JVM internals, Collections framework, Exception handling, Multi-threading, and Streams API.", 1),
                    ("Spring Boot & Dependency Injection", "Spring core, Spring MVC, Component scanning, Autowiring, and application properties.", 2),
                    ("Hibernate & JPA ORM", "Object-relational mapping, entity mappings, criteria queries, and transaction management.", 3),
                    ("Microservices Architecture", "Service discovery with Eureka, API Gateway, Circuit Breaker, and inter-service communication.", 4),
                    ("Enterprise Web Project", "Full stack enterprise portal implementation with JWT authentication and CI/CD pipelines.", 5),
                ]
            },
            {
                "name": "MERN Stack Web Development",
                "duration": "4 Months",
                "fee": 32000.00,
                "description": "Full stack JavaScript development track featuring MongoDB, Express.js, React.js, and Node.js with modern asynchronous patterns and single-page application architectures.",
                "modules": [
                    ("Modern JavaScript (ES6+)", "Arrow functions, destructuring, promises, async/await, modules, and web APIs.", 1),
                    ("React.js Frontend Architecture", "JSX, functional components, hooks (useState, useEffect, useContext), and routing.", 2),
                    ("Node.js & Express.js Backend", "Event-driven architecture, middleware pipeline, RESTful API design, and error handling.", 3),
                    ("NoSQL & Full Stack Integration", "Document data modeling, CRUD pipelines, authentication, and state management.", 4),
                ]
            },
            {
                "name": "Data Science & Artificial Intelligence",
                "duration": "6 Months",
                "fee": 45000.00,
                "description": "Deep dive into statistical analysis, machine learning algorithms, deep learning, NLP, computer vision, and predictive modeling using Python, Pandas, Scikit-learn, and TensorFlow.",
                "modules": [
                    ("Python for Data Analysis", "NumPy, Pandas, Matplotlib, Seaborn, and exploratory data analysis techniques.", 1),
                    ("Applied Machine Learning", "Supervised and unsupervised algorithms: Linear/Logistic regression, Trees, SVM, and Clustering.", 2),
                    ("Deep Learning & Neural Networks", "Artificial Neural Networks, CNN for vision tasks, and TensorFlow / Keras workflows.", 3),
                    ("Natural Language Processing (NLP)", "Text tokenization, sentiment analysis, TF-IDF, Word2Vec, and Transformers.", 4),
                ]
            },
            {
                "name": "Cloud Architecture & DevOps",
                "duration": "4 Months",
                "fee": 35000.00,
                "description": "Master continuous integration and deployment with Docker, Kubernetes, Linux administration, Terraform, GitHub Actions, and AWS cloud infrastructures.",
                "modules": [
                    ("Linux Administration & Shell Scripting", "User permissions, systemd, bash automation, and networking fundamentals.", 1),
                    ("Containerization with Docker", "Dockerfiles, multi-stage builds, networking, volumes, and Docker Compose.", 2),
                    ("Kubernetes Cluster Orchestration", "Pods, Deployments, Services, Ingress, Helm charts, and cluster management.", 3),
                    ("CI/CD Automation & Cloud Infrastructure", "GitHub Actions workflows, Terraform IaC, and AWS EC2/S3/VPC deployment.", 4),
                ]
            },
            {
                "name": "Software Testing & Automation QA",
                "duration": "3 Months",
                "fee": 28000.00,
                "description": "Learn manual testing methodologies, test cases design, defect tracking, and automated testing with Selenium WebDriver, TestNG, and Postman API testing.",
                "modules": [
                    ("Software Testing Fundamentals", "SDLC, STLC, test design techniques, Agile Scrum methodology, and Bugzilla/Jira.", 1),
                    ("Selenium WebDriver Automation", "Locators, WebDriver architecture, TestNG framework, Page Object Model (POM).", 2),
                    ("API Testing with Postman", "REST API inspection, response assertions, authentication testing, and automation runs.", 3),
                ]
            },
        ]

        created_courses = []
        for cdata in courses_catalog:
            course, _ = Course.objects.get_or_create(
                name=cdata["name"],
                defaults={
                    "duration": cdata["duration"],
                    "fee": cdata["fee"],
                    "description": cdata["description"],
                    "is_active": True,
                }
            )
            created_courses.append(course)

            # Syllabuses
            for title, desc, order in cdata["modules"]:
                Syllabus.objects.get_or_create(
                    course=course,
                    order=order,
                    defaults={
                        "title": title,
                        "description": desc,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f"Populated {len(created_courses)} courses with comprehensive syllabus modules."))

        # 6. Placements
        placements_data = [
            ("Rahul Nair", "Tata Consultancy Services (TCS)", "Full Stack Developer"),
            ("Ananya Sharma", "Infosys Technologies", "Python Backend Engineer"),
            ("Arun Kumar", "Wipro Limited", "Cloud & DevOps Specialist"),
            ("Sneha Pillai", "UST Global", "Software Engineer"),
            ("Mohammed Fasil", "Allianz Technology", "Software Test Analyst"),
            ("Keerthi Raj", "Amazon Web Services", "Cloud Associate"),
        ]
        for name, company, role in placements_data:
            Placement.objects.get_or_create(
                name=name,
                company=company,
                defaults={"role": role}
            )
        self.stdout.write(self.style.SUCCESS(f"Populated {len(placements_data)} placement records."))

        # 7. FAQs
        faqs_data = [
            (
                "Are SCOPE INDIA courses beginner-friendly for non-IT graduates?",
                "Yes! All our training tracks start from the foundational building blocks of programming, logic building, and database basics before transitioning into advanced frameworks. Graduates from any academic background can succeed.",
                1
            ),
            (
                "Does SCOPE INDIA provide 100% placement support?",
                "Yes, our dedicated placement wing conducts resume preparation, mock HR/technical interviews, coding tests, and direct referral drives with our 100+ recruitment partners until you secure an offer.",
                2
            ),
            (
                "Can I attend demo sessions before making an enrollment decision?",
                "Absolutely. You can schedule a free counseling and live demo session at any of our training centers or online via Google Meet.",
                3
            ),
            (
                "What is the training methodology followed during the course?",
                "We emphasize 70% practical hands-on coding and 30% conceptual theory. Students work on lab assignments every day and build industrial capstone applications under the mentorship of working IT specialists.",
                4
            ),
            (
                "Will I receive an industry-recognized certificate upon completion?",
                "Yes, SCOPE INDIA provides an ISO 9001:2015 certified Diploma Certificate along with course completion and industrial project experience credentials.",
                5
            ),
            (
                "Are installment fee payment options available for students?",
                "Yes, we provide flexible installment payment plans to ensure quality technology education remains accessible to all aspiring students.",
                6
            ),
        ]
        for q, a, order in faqs_data:
            FAQ.objects.get_or_create(
                question=q,
                defaults={"answer": a, "order": order, "is_active": True}
            )
        self.stdout.write(self.style.SUCCESS(f"Populated {len(faqs_data)} FAQs."))

        # 8. AboutContent
        about_data = [
            (
                "Over a Decade of Empowering IT Careers",
                "Founded with a vision to eliminate the chasm between textbook university curricula and the demanding expectations of global tech giants, SCOPE INDIA has developed into one of South India's premier software and cloud coaching destinations. With centers in Thiruvananthapuram, Kochi, and Nagercoil, we have nurtured more than 10,000 successful IT professionals."
            ),
            (
                "Our Hands-On Pedagogical Philosophy",
                "We reject passive lecture methodologies. At SCOPE INDIA, every aspiring developer writes code from day one. You implement database tables, write backend routing, construct responsive user interfaces, and deploy live applications onto cloud servers."
            ),
        ]
        for title, content in about_data:
            AboutContent.objects.get_or_create(
                title=title,
                defaults={"content": content}
            )
        self.stdout.write(self.style.SUCCESS("Populated AboutContent records."))

        # 9. Superuser / Staff Admin User
        admin_email = "admin@scopeindia.org"
        admin_user, admin_created = User.objects.get_or_create(
            username=admin_email,
            defaults={
                "email": admin_email,
                "first_name": "Scope",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if admin_created:
            admin_user.set_password("Admin@12345")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created Admin account: {admin_email} (Password: Admin@12345)"))
        else:
            self.stdout.write(f"Admin account already exists: {admin_email}")

        # 10. Sample Verified Student User
        student_email = "student@scopeindia.org"
        student_user, stu_created = User.objects.get_or_create(
            username=student_email,
            defaults={
                "email": student_email,
                "first_name": "Anand",
                "last_name": "Menon",
            }
        )
        if stu_created:
            student_user.set_password("Student@12345")
            student_user.save()

            student_profile = Student.objects.create(
                user=student_user,
                first_name="Anand",
                last_name="Menon",
                gender="Male",
                date_of_birth=date(2001, 5, 14),
                phone="9876543210",
                country=india,
                state=state_objs["Kerala"],
                city=city_objs["Thiruvananthapuram"],
                email_verified=True,
                force_password_change=False,
            )
            student_profile.hobbies.set(hobby_objs[:3])

            # Sample Enrollment
            Enrollment.objects.create(
                student=student_profile,
                course=created_courses[0]  # Python Full Stack
            )
            self.stdout.write(self.style.SUCCESS(f"Created Sample Student: {student_email} (Password: Student@12345)"))
        else:
            self.stdout.write(f"Student account already exists: {student_email}")

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully!"))
