from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Author(models.Model):
    """Author of books in the catalog."""
    name = models.CharField(max_length=200, help_text="Author's full name")
    biography = models.TextField(blank=True, help_text="Short author biography or background")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.books.count()


class Book(models.Model):
    """Book inventory and catalog information."""
    GENRE_CHOICES = [
        ('Fiction', 'Fiction'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Computer Science', 'Computer Science & Tech'),
        ('Science', 'Science & Engineering'),
        ('History', 'History & Society'),
        ('Philosophy', 'Philosophy & Psychology'),
        ('Fantasy', 'Fantasy & Sci-Fi'),
        ('Mystery', 'Mystery & Thriller'),
        ('Biography', 'Biography & Memoir'),
        ('Business', 'Business & Economics'),
    ]

    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    isbn = models.CharField(max_length=20, unique=True, verbose_name="ISBN")
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, default='Computer Science')
    description = models.TextField(blank=True, help_text="Brief synopsis or overview of the book")
    total_copies = models.PositiveIntegerField(default=1, help_text="Total inventory count")
    available_copies = models.PositiveIntegerField(default=1, help_text="Currently available copies")
    cover_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL to book cover image (e.g. OpenLibrary or Unsplash)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"{self.title} by {self.author.name}"

    def clean(self):
        if self.available_copies > self.total_copies:
            raise ValidationError("Available copies cannot exceed total copies.")

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def borrowed_copies(self):
        return max(0, self.total_copies - self.available_copies)

    @property
    def fallback_cover_color(self):
        """Deterministically generates a vibrant gradient color for cover fallback."""
        colors = [
            ("from-indigo-600", "to-purple-800"),
            ("from-blue-600", "to-cyan-700"),
            ("from-emerald-600", "to-teal-800"),
            ("from-rose-600", "to-pink-800"),
            ("from-amber-600", "to-orange-800"),
        ]
        return colors[abs(hash(self.title)) % len(colors)]


class Member(models.Model):
    """Library member/patron record."""
    name = models.CharField(max_length=150)
    member_id = models.CharField(max_length=50, unique=True, verbose_name="Member ID")
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    joined_date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['name']
        verbose_name = 'Member'
        verbose_name_plural = 'Members'

    def __str__(self):
        return f"{self.name} ({self.member_id})"

    @property
    def active_records(self):
        return self.circulation_records.filter(returned=False)

    @property
    def active_loans_count(self):
        return self.active_records.count()

    @property
    def overdue_records(self):
        today = timezone.now().date()
        return self.circulation_records.filter(returned=False, due_date__lt=today)

    @property
    def overdue_loans_count(self):
        return self.overdue_records.count()

    @property
    def total_fines_accrued(self):
        total = self.circulation_records.filter(returned=True).aggregate(
            models.Sum('fine_amount')
        )['fine_amount__sum'] or Decimal('0.00')
        return total


class CirculationRecord(models.Model):
    """Tracks book issuance, due dates, returns and overdue fines."""
    FINE_PER_DAY = Decimal('1.00')  # $1.00 per day overdue fine standard

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='circulation_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='circulation_records')
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(help_text="Expected return date (default 14 days after issue)")
    return_date = models.DateField(null=True, blank=True, help_text="Actual return date")
    fine_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Calculated fine for overdue return"
    )
    returned = models.BooleanField(default=False, verbose_name="Returned")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-issue_date', '-id']
        verbose_name = 'Circulation Record'
        verbose_name_plural = 'Circulation Records'

    def __str__(self):
        status = "Returned" if self.returned else "Active"
        return f"{self.book.title} -> {self.member.name} [{status}]"

    def save(self, *args, **kwargs):
        # Default due date to 14 days after issue date if not explicitly set
        if not self.due_date:
            if not self.issue_date:
                self.issue_date = timezone.now().date()
            self.due_date = self.issue_date + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Checks if the loan is overdue."""
        if self.returned:
            return bool(self.return_date and self.return_date > self.due_date)
        today = timezone.now().date()
        return bool(self.due_date and today > self.due_date)

    @property
    def days_overdue(self):
        """Returns the number of days overdue."""
        if not self.due_date:
            return 0
        if self.returned:
            if self.return_date and self.return_date > self.due_date:
                return (self.return_date - self.due_date).days
            return 0
        today = timezone.now().date()
        if today > self.due_date:
            return (today - self.due_date).days
        return 0

    @property
    def current_estimated_fine(self):
        """Current fine estimation based on overdue days."""
        if self.returned:
            return self.fine_amount
        days = self.days_overdue
        return Decimal(days) * self.FINE_PER_DAY

    def compute_return_fine(self, return_date_val=None):
        """Calculate fine based on given return date (defaults to today)."""
        ret_date = return_date_val or timezone.now().date()
        if self.due_date and ret_date > self.due_date:
            days = (ret_date - self.due_date).days
            return Decimal(days) * self.FINE_PER_DAY
        return Decimal('0.00')
