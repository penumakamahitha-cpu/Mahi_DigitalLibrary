from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from .models import Author, Book, Member, CirculationRecord


def create_all_seed_data():
    """Populates realistic seed data for digital library portal."""
    today = timezone.now().date()

    # 1. Authors
    authors_data = [
        {
            'name': 'Robert C. Martin',
            'biography': 'Software craftsman, author of Clean Code, and one of the original signatories of the Agile Manifesto.'
        },
        {
            'name': 'Andrew Hunt & David Thomas',
            'biography': 'Pioneering software consultants and authors of The Pragmatic Programmer.'
        },
        {
            'name': 'Martin Fowler',
            'biography': 'Chief Scientist at ThoughtWorks, author of Refactoring and Patterns of Enterprise Application Architecture.'
        },
        {
            'name': 'Eric Evans',
            'biography': 'Domain-Driven Design thought leader and software architectural practitioner.'
        },
        {
            'name': 'Yuval Noah Harari',
            'biography': 'Historian, philosopher, and bestselling author of Sapiens: A Brief History of Humankind.'
        },
        {
            'name': 'James Clear',
            'biography': 'Author and speaker focused on habits, decision making, and continuous improvement.'
        },
        {
            'name': 'Arthur Conan Doyle',
            'biography': 'British writer and creator of legendary detective Sherlock Holmes.'
        },
    ]

    author_objs = {}
    for a in authors_data:
        obj, _ = Author.objects.get_or_create(name=a['name'], defaults={'biography': a['biography']})
        author_objs[a['name']] = obj

    # 2. Books
    books_data = [
        {
            'title': 'Clean Code: A Handbook of Agile Software Craftsmanship',
            'author': author_objs['Robert C. Martin'],
            'isbn': '978-0132350884',
            'genre': 'Computer Science',
            'total_copies': 5,
            'available_copies': 4,
            'cover_url': 'https://images.unsplash.com/photo-1532012164546-f432f2e37b73?w=500&auto=format&fit=crop&q=80',
            'description': 'Even bad code can function. But if code isn\'t clean, it can bring a development organization to its knees. Every year, countless hours and significant resources are lost because of poorly written code.'
        },
        {
            'title': 'The Pragmatic Programmer: Your Journey to Mastery',
            'author': author_objs['Andrew Hunt & David Thomas'],
            'isbn': '978-0135957059',
            'genre': 'Computer Science',
            'total_copies': 4,
            'available_copies': 3,
            'cover_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80',
            'description': 'The Pragmatic Programmer cuts through the increasing specialization and technicalities of modern software development to examine the core process.'
        },
        {
            'title': 'Refactoring: Improving the Design of Existing Code',
            'author': author_objs['Martin Fowler'],
            'isbn': '978-0134757599',
            'genre': 'Computer Science',
            'total_copies': 3,
            'available_copies': 3,
            'cover_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80',
            'description': 'For more than twenty years, serious programmers have relied on Martin Fowler\'s Refactoring to improve the design of existing code and enhance software maintainability.'
        },
        {
            'title': 'Domain-Driven Design: Tackling Complexity in Software',
            'author': author_objs['Eric Evans'],
            'isbn': '978-0321125217',
            'genre': 'Computer Science',
            'total_copies': 2,
            'available_copies': 0,  # Zero available copies to test zero inventory validation!
            'cover_url': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=500&auto=format&fit=crop&q=80',
            'description': 'Leading software design principles showing how a systematic domain-driven approach connects implementation directly to an evolving model.'
        },
        {
            'title': 'Sapiens: A Brief History of Humankind',
            'author': author_objs['Yuval Noah Harari'],
            'isbn': '978-0062316097',
            'genre': 'History',
            'total_copies': 6,
            'available_copies': 5,
            'cover_url': 'https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80',
            'description': 'One hundred thousand years ago, at least six different species of humans inhabited Earth. Yet today there is only one—Homo sapiens.'
        },
        {
            'title': 'Atomic Habits: An Easy & Proven Way to Build Good Habits',
            'author': author_objs['James Clear'],
            'isbn': '978-0735211292',
            'genre': 'Philosophy',
            'total_copies': 5,
            'available_copies': 5,
            'cover_url': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=500&auto=format&fit=crop&q=80',
            'description': 'No matter your goals, Atomic Habits offers a proven framework for improving—every day. Learn practical strategies to form good habits and break bad ones.'
        },
        {
            'title': 'The Adventures of Sherlock Holmes',
            'author': author_objs['Arthur Conan Doyle'],
            'isbn': '978-0141034355',
            'genre': 'Mystery',
            'total_copies': 4,
            'available_copies': 4,
            'cover_url': 'https://images.unsplash.com/photo-1507842229451-7f01be7fe86c?w=500&auto=format&fit=crop&q=80',
            'description': 'A classic collection of twelve detective mystery stories featuring the world-famous investigator Sherlock Holmes and Dr. John Watson.'
        },
    ]

    book_objs = {}
    for b in books_data:
        obj, _ = Book.objects.get_or_create(
            isbn=b['isbn'],
            defaults={
                'title': b['title'],
                'author': b['author'],
                'genre': b['genre'],
                'total_copies': b['total_copies'],
                'available_copies': b['available_copies'],
                'cover_url': b['cover_url'],
                'description': b['description'],
            }
        )
        book_objs[b['isbn']] = obj

    # 3. Members
    members_data = [
        {
            'name': 'Eleanor Vance',
            'member_id': 'MEM-1001',
            'email': 'eleanor.vance@library.org',
            'phone': '+1 (555) 234-5678',
            'joined_date': today - timedelta(days=120)
        },
        {
            'name': 'Marcus Chen',
            'member_id': 'MEM-1002',
            'email': 'marcus.chen@library.org',
            'phone': '+1 (555) 345-6789',
            'joined_date': today - timedelta(days=90)
        },
        {
            'name': 'Sophia Rodriguez',
            'member_id': 'MEM-1003',
            'email': 'sophia.r@library.org',
            'phone': '+1 (555) 456-7890',
            'joined_date': today - timedelta(days=60)
        },
        {
            'name': 'David Kim',
            'member_id': 'MEM-1004',
            'email': 'david.kim@library.org',
            'phone': '+1 (555) 567-8901',
            'joined_date': today - timedelta(days=30)
        },
    ]

    member_objs = {}
    for m in members_data:
        obj, _ = Member.objects.get_or_create(
            member_id=m['member_id'],
            defaults={
                'name': m['name'],
                'email': m['email'],
                'phone': m['phone'],
                'joined_date': m['joined_date'],
            }
        )
        member_objs[m['member_id']] = obj

    # 4. Circulation Records
    # If no records exist yet, create active normal, active overdue, and returned records
    if CirculationRecord.objects.count() == 0:
        # A) Normal active loan (due in 8 days)
        CirculationRecord.objects.create(
            book=book_objs['978-0132350884'],  # Clean Code
            member=member_objs['MEM-1001'],
            issue_date=today - timedelta(days=6),
            due_date=today + timedelta(days=8),
            returned=False,
            notes='Initial checkout in pristine condition.'
        )

        # B) OVERDUE active loan (due 10 days ago -> $10 fine accumulated)
        CirculationRecord.objects.create(
            book=book_objs['978-0321125217'],  # DDD (has 0 copies available)
            member=member_objs['MEM-1001'],
            issue_date=today - timedelta(days=24),
            due_date=today - timedelta(days=10),
            returned=False,
            notes='Patron notified via email on Day 5 past due date.'
        )

        # C) Another OVERDUE active loan (due 4 days ago -> $4 fine)
        CirculationRecord.objects.create(
            book=book_objs['978-0135957059'],  # Pragmatic Programmer
            member=member_objs['MEM-1002'],
            issue_date=today - timedelta(days=18),
            due_date=today - timedelta(days=4),
            returned=False,
            notes='Reserved loan extension requested.'
        )

        # D) Normal active loan
        CirculationRecord.objects.create(
            book=book_objs['978-0062316097'],  # Sapiens
            member=member_objs['MEM-1003'],
            issue_date=today - timedelta(days=3),
            due_date=today + timedelta(days=11),
            returned=False,
            notes='Standard student checkout.'
        )

        # E) Past Returned record with $3 fine paid
        CirculationRecord.objects.create(
            book=book_objs['978-0134757599'],  # Refactoring
            member=member_objs['MEM-1003'],
            issue_date=today - timedelta(days=45),
            due_date=today - timedelta(days=31),
            return_date=today - timedelta(days=28),
            fine_amount=Decimal('3.00'),
            returned=True,
            notes='Returned 3 days late. Fine of $3.00 received.'
        )

        # F) Past Returned record on time with $0 fine
        CirculationRecord.objects.create(
            book=book_objs['978-0735211292'],  # Atomic Habits
            member=member_objs['MEM-1004'],
            issue_date=today - timedelta(days=30),
            due_date=today - timedelta(days=16),
            return_date=today - timedelta(days=18),
            fine_amount=Decimal('0.00'),
            returned=True,
            notes='Returned early in great condition.'
        )

    return True
