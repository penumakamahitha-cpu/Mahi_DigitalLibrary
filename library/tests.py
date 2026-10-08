from datetime import timedelta, date
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from library.models import Author, Book, Member, CirculationRecord


class LibrarySystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.today = timezone.now().date()

        # Create author
        self.author = Author.objects.create(
            name="Robert C. Martin",
            biography="Author of Clean Code."
        )

        # Create book with 2 total, 2 available copies
        self.book = Book.objects.create(
            title="Clean Code",
            author=self.author,
            isbn="978-0132350884",
            genre="Computer Science",
            total_copies=2,
            available_copies=2,
            cover_url="https://example.com/cover.jpg"
        )

        # Create member
        self.member = Member.objects.create(
            name="Jane Doe",
            member_id="MEM-9001",
            email="jane@example.com",
            phone="+1 555-0100",
            joined_date=self.today
        )

    def test_default_due_date_and_issue_workflow(self):
        """Test business logic: available copies decrease and due date defaults to 14 days."""
        response = self.client.post(reverse('issue_book'), {
            'book': self.book.id,
            'member': self.member.id,
            'issue_date': self.today.strftime('%Y-%m-%d'),
            'due_date': (self.today + timedelta(days=14)).strftime('%Y-%m-%d'),
            'notes': 'Test issue'
        })

        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)

        record = CirculationRecord.objects.get(book=self.book, member=self.member)
        self.assertFalse(record.returned)
        self.assertEqual(record.due_date, self.today + timedelta(days=14))

    def test_cannot_issue_when_out_of_stock(self):
        """Test business logic: cannot issue a book when available_copies is 0."""
        self.book.available_copies = 0
        self.book.save()

        response = self.client.post(reverse('issue_book'), {
            'book': self.book.id,
            'member': self.member.id,
            'issue_date': self.today.strftime('%Y-%m-%d'),
            'due_date': (self.today + timedelta(days=14)).strftime('%Y-%m-%d'),
        })

        # Form should fail validation and not create record
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 0)
        self.assertEqual(CirculationRecord.objects.filter(book=self.book).count(), 0)

    def test_return_workflow_and_fine_calculation_on_time(self):
        """Test returning a book on time: available copies increment, fine is 0."""
        self.book.available_copies = 1
        self.book.save()

        record = CirculationRecord.objects.create(
            book=self.book,
            member=self.member,
            issue_date=self.today - timedelta(days=5),
            due_date=self.today + timedelta(days=9),
            returned=False
        )

        response = self.client.post(reverse('return_book', args=[record.id]), {
            'return_date': self.today.strftime('%Y-%m-%d'),
            'fine_amount': '0.00',
            'notes': 'Good condition'
        })

        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

        record.refresh_from_db()
        self.assertTrue(record.returned)
        self.assertEqual(record.fine_amount, Decimal('0.00'))
        self.assertFalse(record.is_overdue)

    def test_return_workflow_and_fine_calculation_overdue(self):
        """Test returning an overdue book: fine is calculated ($1.00/day)."""
        self.book.available_copies = 1
        self.book.save()

        # Issued 20 days ago, due 6 days ago
        record = CirculationRecord.objects.create(
            book=self.book,
            member=self.member,
            issue_date=self.today - timedelta(days=20),
            due_date=self.today - timedelta(days=6),
            returned=False
        )

        self.assertTrue(record.is_overdue)
        self.assertEqual(record.days_overdue, 6)

        # Return today (6 days late)
        response = self.client.post(reverse('return_book', args=[record.id]), {
            'return_date': self.today.strftime('%Y-%m-%d'),
            'fine_amount': '6.00',
            'notes': 'Paid in cash'
        })

        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)

        record.refresh_from_db()
        self.assertTrue(record.returned)
        self.assertEqual(record.fine_amount, Decimal('6.00'))

    def test_catalog_view_and_search(self):
        """Test catalog page and search filter."""
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Code")

        # Test search query
        response = self.client.get(reverse('catalog') + '?q=Clean')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clean Code")

        # Test unmatched query
        response = self.client.get(reverse('catalog') + '?q=NonExistentTitle')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Clean Code")

    def test_member_dashboard(self):
        """Test member dashboard displays patron info and loan metrics."""
        record = CirculationRecord.objects.create(
            book=self.book,
            member=self.member,
            issue_date=self.today - timedelta(days=25),
            due_date=self.today - timedelta(days=11),
            returned=False
        )

        response = self.client.get(reverse('member_dashboard', args=[self.member.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jane Doe")
        self.assertContains(response, "MEM-9001")
        self.assertContains(response, "Overdue Circulation Alert")
        self.assertContains(response, "$11.00")

    def test_calculator_page(self):
        """Test calculator page loads successfully."""
        response = self.client.get(reverse('calculator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interactive Due-Date & Overdue Fine Calculator")
