"""
GARL Seed Data Command
Usage: python manage.py seed_data

Creates realistic demo data for development and testing.
All demo records are clearly marked. Run only in development.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seeds the database with demo data for development.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding GARL demo data...'))

        self._seed_subjects()
        self._seed_users()
        self._seed_institutions()
        self._seed_research_categories()
        self._seed_research_papers()
        self._seed_publication_types()
        self._seed_journals()
        self._seed_books()
        self._seed_innovation_categories()
        self._seed_innovation_projects()
        self._seed_course_categories()
        self._seed_courses()
        self._seed_health_categories()
        self._seed_health_resources()
        self._seed_event_categories()
        self._seed_events()
        self._seed_faqs()

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))

    # ── Subjects ────────────────────────────────────────────────────────────
    def _seed_subjects(self):
        from core.models import Subject
        subjects = [
            ('Computer Science', 'bi-cpu', '#0d6efd'),
            ('Engineering', 'bi-gear', '#6c757d'),
            ('Medicine', 'bi-heart-pulse', '#dc3545'),
            ('Nursing', 'bi-hospital', '#0dcaf0'),
            ('Pharmacy', 'bi-capsule', '#198754'),
            ('Agriculture', 'bi-tree', '#20c997'),
            ('Business & Economics', 'bi-briefcase', '#ffc107'),
            ('Education', 'bi-mortarboard', '#0d6efd'),
            ('Law', 'bi-scales', '#6f42c1'),
            ('Social Sciences', 'bi-people', '#fd7e14'),
            ('Natural Sciences', 'bi-flask', '#20c997'),
            ('Artificial Intelligence', 'bi-robot', '#0d6efd'),
            ('Data Science', 'bi-bar-chart', '#198754'),
            ('Public Health', 'bi-shield-check', '#0dcaf0'),
            ('Environmental Science', 'bi-globe', '#198754'),
            ('Information Technology', 'bi-laptop', '#6c757d'),
            ('Mathematics', 'bi-calculator', '#6f42c1'),
            ('Physics', 'bi-lightning', '#ffc107'),
            ('Chemistry', 'bi-droplet', '#dc3545'),
            ('Biology', 'bi-bug', '#20c997'),
        ]
        for name, icon, color in subjects:
            Subject.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'color': color}
            )
        self.stdout.write('  ✓ Subjects')

    # ── Users ───────────────────────────────────────────────────────────────
    def _seed_users(self):
        from accounts.models import User, RoleType
        demo_users = [
            ('admin@garl.edu',      'Admin',    'User',       'gadmin',      RoleType.SUPER_ADMIN,   'Admin1234!'),
            ('researcher@garl.edu', 'Dr. Jane', 'Osei',       'janosei',     RoleType.RESEARCHER,    'Demo1234!'),
            ('author@garl.edu',     'Prof. Kwame','Mensah',   'kwamem',      RoleType.AUTHOR,        'Demo1234!'),
            ('student@garl.edu',    'Ama',      'Boateng',    'aboateng',    RoleType.STUDENT,       'Demo1234!'),
            ('instructor@garl.edu', 'Dr. Eric', 'Asante',     'easante',     RoleType.INSTRUCTOR,    'Demo1234!'),
            ('editor@garl.edu',     'Grace',    'Owusu',      'gowusu',      RoleType.EDITOR,        'Demo1234!'),
            ('reviewer@garl.edu',   'Prof. Sam','Darko',      'sdarko',      RoleType.REVIEWER,      'Demo1234!'),
            ('institution@garl.edu','University','Admin',     'uniadmin',    RoleType.INSTITUTION_ADMIN,'Demo1234!'),
        ]
        for email, first, last, username, role, pwd in demo_users:
            if not User.objects.filter(email=email).exists():
                u = User.objects.create_user(
                    email=email, password=pwd,
                    first_name=first, last_name=last,
                    username=username, role=role,
                    is_verified=True
                )
                if role == RoleType.SUPER_ADMIN:
                    u.is_staff = True
                    u.is_superuser = True
                    u.save()
        self.stdout.write('  ✓ Demo users')

    # ── Institutions ─────────────────────────────────────────────────────────
    def _seed_institutions(self):
        from community.models import Institution, InstitutionType
        from accounts.models import User

        itype, _ = InstitutionType.objects.get_or_create(name='University')
        inst_type2, _ = InstitutionType.objects.get_or_create(name='Research Institute')
        inst_type3, _ = InstitutionType.objects.get_or_create(name='Library')

        admin_user = User.objects.filter(role='institution_admin').first()

        institutions = [
            ('University of Global Sciences', 'UGS', itype, 'Ghana', 'Accra', 'www.ugs.edu.gh', 1948),
            ('African Institute of Technology', 'AIT', itype, 'Kenya', 'Nairobi', 'www.ait.ac.ke', 1965),
            ('Global Health Research Centre', 'GHRC', inst_type2, 'Nigeria', 'Lagos', 'www.ghrc.ng', 2001),
            ('Pan-African Academic Library', 'PAL', inst_type3, 'South Africa', 'Cape Town', 'www.pal.org.za', 1990),
            ('Institute of Innovation & Technology', 'IIT', inst_type2, 'Rwanda', 'Kigali', 'www.iit.rw', 2010),
        ]
        for name, abbr, itype_obj, country, city, web, year in institutions:
            Institution.objects.get_or_create(
                name=name,
                defaults={
                    'institution_type': itype_obj,
                    'country': country, 'city': city,
                    'website': f'https://{web}',
                    'established_year': year,
                    'is_published': True, 'is_verified': True,
                    'admin_user': admin_user,
                    'description': f'[DEMO] {name} is a leading academic institution in {country}.',
                }
            )
        self.stdout.write('  ✓ Institutions')

    # ── Research categories ───────────────────────────────────────────────────
    def _seed_research_categories(self):
        from research.models import ResearchCategory
        cats = [
            'Computer Science & IT', 'Medical Sciences', 'Agricultural Sciences',
            'Engineering & Technology', 'Social Sciences & Humanities',
            'Natural Sciences', 'Business & Management', 'Education & Pedagogy',
            'Environmental Studies', 'Public Health & Epidemiology',
        ]
        for name in cats:
            ResearchCategory.objects.get_or_create(name=name)
        self.stdout.write('  ✓ Research categories')

    # ── Research papers ───────────────────────────────────────────────────────
    def _seed_research_papers(self):
        from research.models import ResearchPaper, ResearchCategory
        from accounts.models import User

        researcher = User.objects.filter(role='researcher').first()
        cat = ResearchCategory.objects.first()
        papers = [
            ('[DEMO] Artificial Intelligence in Healthcare: A Systematic Review',
             'This paper reviews AI applications in clinical diagnostics, drug discovery, and patient care management.',
             'AI, healthcare, machine learning, clinical decision support'),
            ('[DEMO] Climate Change Impact on Agricultural Productivity in Sub-Saharan Africa',
             'An empirical study examining the correlation between rising temperatures and crop yields.',
             'climate change, agriculture, food security, Sub-Saharan Africa'),
            ('[DEMO] Blockchain Technology in Academic Credential Verification',
             'Explores the use of distributed ledger technology for secure and verifiable academic credentials.',
             'blockchain, credentials, verification, higher education'),
            ('[DEMO] Deep Learning for Natural Language Processing in Low-Resource Languages',
             'Proposes novel architectures for NLP in African languages with limited training data.',
             'deep learning, NLP, African languages, transfer learning'),
            ('[DEMO] The Role of Community Health Workers in Reducing Child Mortality',
             'Evaluates community health interventions and their measurable impact on child health outcomes.',
             'community health, child mortality, public health, Africa'),
            ('[DEMO] Renewable Energy Adoption in Developing Economies',
             'Examines barriers and opportunities for solar and wind energy deployment in emerging markets.',
             'renewable energy, solar, developing countries, policy'),
        ]
        for title, abstract, keywords in papers:
            sl = slugify(title)[:490]
            if not ResearchPaper.objects.filter(slug=sl).exists():
                p = ResearchPaper.objects.create(
                    title=title, abstract=abstract, keywords=keywords,
                    created_by=researcher, status='published',
                    publication_year=2024, language='English',
                    journal_name='GARL Demo Journal',
                    published_at=timezone.now()
                )
                if cat:
                    p.categories.add(cat)
                if researcher:
                    p.authors.add(researcher)
        self.stdout.write('  ✓ Research papers')

    # ── Publication types ─────────────────────────────────────────────────────
    def _seed_publication_types(self):
        from publishing.models import PublicationType
        types = ['Journal Article', 'Book', 'Conference Paper', 'Thesis',
                 'Dissertation', 'Research Report', 'Book Chapter', 'Working Paper']
        for name in types:
            PublicationType.objects.get_or_create(name=name)
        self.stdout.write('  ✓ Publication types')

    # ── Journals ──────────────────────────────────────────────────────────────
    def _seed_journals(self):
        from publishing.models import Journal
        from core.models import Subject
        journals = [
            ('[DEMO] African Journal of Computer Science', '2345-6789', True),
            ('[DEMO] Global Health Research Journal', '2345-7890', True),
            ('[DEMO] Journal of Agricultural Innovation', '2345-8901', True),
            ('[DEMO] Pan-African Engineering Review', '2345-9012', False),
            ('[DEMO] International Education Research Journal', '2345-0123', True),
        ]
        cs_subject = Subject.objects.filter(name='Computer Science').first()
        for title, issn, oa in journals:
            j, _ = Journal.objects.get_or_create(
                title=title,
                defaults={
                    'issn': issn, 'is_open_access': oa,
                    'is_active': True,
                    'description': f'[DEMO] {title} — a leading peer-reviewed academic journal.',
                    'publisher': 'GARL Demo Publisher',
                }
            )
            if cs_subject:
                j.subjects.add(cs_subject)
        self.stdout.write('  ✓ Journals')

    # ── Books ─────────────────────────────────────────────────────────────────
    def _seed_books(self):
        from publishing.models import Book
        from accounts.models import User
        admin = User.objects.filter(is_superuser=True).first()
        books = [
            ('[DEMO] Introduction to Artificial Intelligence', '978-0-000001-00-1', 'GARL Press', 2023),
            ('[DEMO] Clinical Pharmacology for Nursing Students', '978-0-000002-00-2', 'GARL Medical', 2022),
            ('[DEMO] Sustainable Agriculture: Principles and Practice', '978-0-000003-00-3', 'GARL Press', 2023),
            ('[DEMO] Data Science Fundamentals', '978-0-000004-00-4', 'GARL Tech', 2024),
            ('[DEMO] Public Health Policy in Africa', '978-0-000005-00-5', 'GARL Press', 2023),
            ('[DEMO] Engineering Mathematics', '978-0-000006-00-6', 'GARL Press', 2022),
        ]
        for title, isbn, publisher, year in books:
            Book.objects.get_or_create(
                title=title,
                defaults={
                    'isbn': isbn, 'publisher': publisher, 'year': year,
                    'is_free': True, 'is_published': True,
                    'language': 'English',
                    'description': f'[DEMO] {title}. A comprehensive academic resource.',
                    'added_by': admin,
                }
            )
        self.stdout.write('  ✓ Books')

    # ── Innovation categories ─────────────────────────────────────────────────
    def _seed_innovation_categories(self):
        from innovation.models import ProjectCategory
        cats = [
            ('AgriTech', 'bi-tree'),
            ('HealthTech', 'bi-heart-pulse'),
            ('EdTech', 'bi-mortarboard'),
            ('FinTech', 'bi-credit-card'),
            ('CleanEnergy', 'bi-sun'),
            ('AI & Machine Learning', 'bi-robot'),
            ('Mobile & Web Apps', 'bi-phone'),
            ('IoT & Hardware', 'bi-cpu'),
        ]
        for name, icon in cats:
            ProjectCategory.objects.get_or_create(name=name, defaults={'icon': icon})
        self.stdout.write('  ✓ Innovation categories')

    # ── Innovation projects ───────────────────────────────────────────────────
    def _seed_innovation_projects(self):
        from innovation.models import InnovationProject, ProjectCategory
        from accounts.models import User

        student = User.objects.filter(role='student').first()
        researcher = User.objects.filter(role='researcher').first()
        cat = ProjectCategory.objects.filter(name='AI & Machine Learning').first()

        projects = [
            ('[DEMO] AI-Powered Crop Disease Detection App',
             'A mobile app that uses computer vision to detect crop diseases from leaf photographs.',
             'Python, TensorFlow, React Native', 'student', student),
            ('[DEMO] Smart Water Quality Monitoring System',
             'IoT-based real-time water quality monitoring for rural communities.',
             'Arduino, Python, MQTT, React', 'prototype', researcher),
            ('[DEMO] Blockchain-Based Land Registry',
             'Decentralized land ownership records to reduce fraud and disputes.',
             'Ethereum, Solidity, React, Node.js', 'research', researcher),
            ('[DEMO] Telemedicine Platform for Rural Health',
             'Low-bandwidth video consultation platform for remote communities.',
             'Django, WebRTC, React', 'startup', student),
        ]
        for title, desc, tech, ptype, user in projects:
            sl = slugify(title)[:400]
            if not InnovationProject.objects.filter(slug=sl).exists():
                p = InnovationProject.objects.create(
                    title=title, description=desc, technologies=tech,
                    project_type=ptype, submitted_by=user,
                    status='published', is_featured=True,
                    institution='University of Global Sciences',
                    published_at=timezone.now()
                )
                if cat:
                    p.categories.add(cat)
        self.stdout.write('  ✓ Innovation projects')

    # ── Course categories ─────────────────────────────────────────────────────
    def _seed_course_categories(self):
        from learning.models import CourseCategory
        cats = [
            ('Computer Science', 'bi-cpu'),
            ('Health Sciences', 'bi-heart-pulse'),
            ('Data Science', 'bi-bar-chart'),
            ('Engineering', 'bi-gear'),
            ('Business', 'bi-briefcase'),
            ('Languages', 'bi-translate'),
            ('Agriculture', 'bi-tree'),
            ('Research Methods', 'bi-search'),
        ]
        for name, icon in cats:
            CourseCategory.objects.get_or_create(name=name, defaults={'icon': icon})
        self.stdout.write('  ✓ Course categories')

    # ── Courses ───────────────────────────────────────────────────────────────
    def _seed_courses(self):
        from learning.models import Course, CourseCategory, Lesson
        from accounts.models import User

        instructor = User.objects.filter(role='instructor').first()
        cs_cat  = CourseCategory.objects.filter(name='Computer Science').first()
        ds_cat  = CourseCategory.objects.filter(name='Data Science').first()
        hs_cat  = CourseCategory.objects.filter(name='Health Sciences').first()

        courses_data = [
            ('[DEMO] Python for Data Science', cs_cat, 'beginner', True, True),
            ('[DEMO] Introduction to Machine Learning', ds_cat, 'intermediate', True, True),
            ('[DEMO] Medical Terminology for Nursing', hs_cat, 'beginner', True, False),
            ('[DEMO] Academic Research Methods', None, 'beginner', True, True),
            ('[DEMO] Clinical Pharmacology Essentials', hs_cat, 'intermediate', True, True),
        ]
        for title, cat, level, featured, cert in courses_data:
            sl = slugify(title)[:400]
            if not Course.objects.filter(slug=sl).exists():
                c = Course.objects.create(
                    title=title, category=cat, level=level,
                    instructor=instructor, is_published=True,
                    is_featured=featured, is_free=True,
                    has_certificate=cert, language='English',
                    description=f'[DEMO] {title}. A comprehensive course covering key concepts.',
                    duration_hours=20,
                )
                # Add demo lessons
                for i, lesson_title in enumerate([
                    'Introduction & Overview',
                    'Core Concepts',
                    'Practical Applications',
                    'Case Studies',
                    'Assessment & Review',
                ], start=1):
                    Lesson.objects.create(
                        course=c, title=f'[DEMO] {lesson_title}',
                        content_type='text', order=i,
                        content=f'[DEMO CONTENT] This is lesson {i} of {c.title}. Real content goes here.',
                        is_published=True,
                    )
        self.stdout.write('  ✓ Courses with lessons')

    # ── Health categories ─────────────────────────────────────────────────────
    def _seed_health_categories(self):
        from health_science.models import HealthCategory
        cats = [
            ('Nursing Fundamentals', 'nursing', 'bi-hospital'),
            ('Clinical Medicine', 'medicine', 'bi-heart-pulse'),
            ('Obstetrics & Midwifery', 'midwifery', 'bi-person-hearts'),
            ('Clinical Pharmacy', 'pharmacy', 'bi-capsule'),
            ('Oral Health', 'dentistry', 'bi-emoji-smile'),
            ('Epidemiology', 'public_health', 'bi-shield-check'),
            ('Medical Laboratory Science', 'biomedical', 'bi-flask'),
            ('Physiotherapy', 'allied_health', 'bi-person-walking'),
        ]
        for name, disc, icon in cats:
            HealthCategory.objects.get_or_create(
                name=name, defaults={'discipline': disc, 'icon': icon, 'is_active': True}
            )
        self.stdout.write('  ✓ Health categories')

    # ── Health resources ──────────────────────────────────────────────────────
    def _seed_health_resources(self):
        from health_science.models import HealthResource, HealthCategory
        from accounts.models import User

        admin = User.objects.filter(is_superuser=True).first()
        nursing_cat = HealthCategory.objects.filter(discipline='nursing').first()
        medicine_cat = HealthCategory.objects.filter(discipline='medicine').first()

        resources = [
            ('[DEMO] Fundamentals of Nursing Care', nursing_cat, 'textbook',
             'Comprehensive guide to nursing fundamentals and patient care.'),
            ('[DEMO] Clinical Assessment in Primary Healthcare', medicine_cat, 'guideline',
             'Evidence-based clinical assessment protocols for primary care settings.'),
            ('[DEMO] Drug Interactions in Polypharmacy', None, 'paper',
             'Research review on common drug interactions in elderly patients.'),
            ('[DEMO] Maternal Health Outcomes in Rural Africa', None, 'paper',
             'Systematic review of maternal mortality reduction strategies.'),
            ('[DEMO] Introduction to Epidemiology — Lecture Notes', None, 'lecture',
             'Core concepts of epidemiology including incidence, prevalence, and study designs.'),
        ]
        for title, cat, rtype, desc in resources:
            sl = slugify(title)[:400]
            if not HealthResource.objects.filter(slug=sl).exists():
                HealthResource.objects.create(
                    title=title, category=cat, resource_type=rtype,
                    description=desc, is_published=True,
                    language='English', added_by=admin,
                )
        self.stdout.write('  ✓ Health resources')

    # ── Event categories ──────────────────────────────────────────────────────
    def _seed_event_categories(self):
        from events.models import EventCategory
        for name in ['Academic Conference', 'Workshop', 'Webinar', 'Innovation Challenge', 'Seminar']:
            EventCategory.objects.get_or_create(name=name)
        self.stdout.write('  ✓ Event categories')

    # ── Events ────────────────────────────────────────────────────────────────
    def _seed_events(self):
        from events.models import Event
        from accounts.models import User

        organizer = User.objects.filter(is_superuser=True).first()
        now       = timezone.now()

        events_data = [
            ('[DEMO] International Conference on AI in Healthcare',
             'conference', now + timedelta(days=30), now + timedelta(days=32),
             'Accra, Ghana', False, 500),
            ('[DEMO] Workshop: Research Methods for Postgraduate Students',
             'workshop', now + timedelta(days=7), now + timedelta(days=7, hours=8),
             'Online (Zoom)', True, 100),
            ('[DEMO] Innovation Challenge: Solutions for Rural Health',
             'competition', now + timedelta(days=60), now + timedelta(days=62),
             'Nairobi, Kenya', False, 200),
            ('[DEMO] Webinar: Publishing in High-Impact Journals',
             'webinar', now + timedelta(days=14), now + timedelta(days=14, hours=2),
             'Online', True, 1000),
            ('[DEMO] Annual Academic Research Symposium',
             'conference', now + timedelta(days=90), now + timedelta(days=92),
             'Lagos, Nigeria', False, 300),
        ]
        for title, etype, start, end, location, online, capacity in events_data:
            sl = slugify(title)[:400]
            if not Event.objects.filter(slug=sl).exists():
                Event.objects.create(
                    title=title, event_type=etype,
                    start_date=start, end_date=end,
                    location=location, is_online=online,
                    capacity=capacity, is_free=True,
                    is_published=True, organizer=organizer,
                    description=f'[DEMO] {title}. Join us for this academic event.',
                )
        self.stdout.write('  ✓ Events')

    # ── FAQs ──────────────────────────────────────────────────────────────────
    def _seed_faqs(self):
        from support.models import FAQCategory, FAQ
        categories_faqs = {
            'Account & Registration': [
                ('How do I create an account on GARL?',
                 'Click "Register" on the homepage, fill in your details, select your role, and submit the form.'),
                ('I forgot my password. How can I reset it?',
                 'Click "Forgot Password" on the login page and follow the instructions sent to your email.'),
                ('Can I change my role after registering?',
                 'Role changes require an administrator. Contact support with a request.'),
            ],
            'Research & Publications': [
                ('How do I submit a research paper?',
                 'Log in, navigate to Publishing Center > Submit, fill in the form and upload your manuscript.'),
                ('How long does the review process take?',
                 'The review process typically takes 2–4 weeks depending on reviewer availability.'),
                ('Can I download research papers for free?',
                 'Open access papers can be downloaded freely. Some resources may require registration.'),
            ],
            'Learning Center': [
                ('How do I enroll in a course?',
                 'Visit a course page and click "Enroll". You can start learning immediately.'),
                ('Will I receive a certificate after completing a course?',
                 'Courses marked with "Certificate" issue digital certificates upon successful completion.'),
            ],
            'Technical Support': [
                ('What file formats can I upload?',
                 'PDF and Word documents are supported for manuscripts. Images must be JPG, PNG, or WebP.'),
                ('The file upload is not working. What should I do?',
                 'Check your file size (max 50MB) and format. If the issue persists, contact technical support.'),
            ],
        }
        for cat_name, faqs in categories_faqs.items():
            cat, _ = FAQCategory.objects.get_or_create(name=cat_name)
            for i, (question, answer) in enumerate(faqs, start=1):
                FAQ.objects.get_or_create(
                    question=question,
                    defaults={'answer': answer, 'category': cat, 'order': i, 'is_published': True}
                )
        self.stdout.write('  ✓ FAQs')
