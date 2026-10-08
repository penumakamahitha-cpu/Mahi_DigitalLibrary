from datetime import date, timedelta
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.http import JsonResponse

from .models import Author, Book, Member, CirculationRecord
from .forms import BookIssueForm, BookReturnForm, BookForm, MemberForm, AuthorForm


def book_catalog(request):
    """
    Catalog view with instant search, genre filtering,
    availability counters, and quick issue links.
    """
    genre_filter = request.GET.get('genre', '')
    availability_filter = request.GET.get('availability', '')
    query = request.GET.get('q', '')

    books = Book.objects.select_related('author').all()

    if genre_filter:
        books = books.filter(genre=genre_filter)

    if availability_filter == 'available':
        books = books.filter(available_copies__gt=0)
    elif availability_filter == 'unavailable':
        books = books.filter(available_copies=0)

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(isbn__icontains=query) |
            Q(genre__icontains=query)
        )

    # Aggregated metrics for stats ribbon
    total_titles = Book.objects.count()
    total_copies_sum = Book.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    available_copies_sum = Book.objects.aggregate(avail=Sum('available_copies'))['avail'] or 0
    active_loans_count = CirculationRecord.objects.filter(returned=False).count()
    overdue_loans_count = CirculationRecord.objects.filter(
        returned=False, due_date__lt=timezone.now().date()
    ).count()

    genres = Book.GENRE_CHOICES

    context = {
        'books': books,
        'genres': genres,
        'selected_genre': genre_filter,
        'selected_availability': availability_filter,
        'search_query': query,
        'total_titles': total_titles,
        'total_copies_sum': total_copies_sum,
        'available_copies_sum': available_copies_sum,
        'active_loans_count': active_loans_count,
        'overdue_loans_count': overdue_loans_count,
    }
    return render(request, 'library/catalog.html', context)


def book_detail(request, pk):
    """Detailed view for an individual book and its active circulation history."""
    book = get_object_or_404(Book.objects.select_related('author'), pk=pk)
    active_records = book.circulation_records.filter(returned=False).select_related('member')
    past_records = book.circulation_records.filter(returned=True).select_related('member')[:10]

    context = {
        'book': book,
        'active_records': active_records,
        'past_records': past_records,
    }
    return render(request, 'library/book_detail.html', context)


def issue_book(request):
    """
    Book issue workflow:
    - Enforces available_copies > 0
    - Decrements available_copies
    - Defaults due_date to 14 days after issue_date
    """
    initial_data = {}
    preselected_book_id = request.GET.get('book_id')
    preselected_member_id = request.GET.get('member_id')

    if preselected_book_id:
        initial_data['book'] = preselected_book_id
    if preselected_member_id:
        initial_data['member'] = preselected_member_id

    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            book = record.book

            # Safety check: do not issue if available_copies is 0
            if book.available_copies <= 0:
                messages.error(request, f"Error: '{book.title}' has no copies available for issue.")
                return render(request, 'library/issue_book.html', {'form': form})

            # Reduce available copies by 1
            book.available_copies -= 1
            book.save()

            # Ensure due_date is set (defaults to issue_date + 14 days if left empty)
            if not record.due_date:
                record.due_date = record.issue_date + timedelta(days=14)

            record.returned = False
            record.fine_amount = Decimal('0.00')
            record.save()

            messages.success(
                request,
                f"Successfully issued '{book.title}' to {record.member.name}. Due Date: {record.due_date.strftime('%B %d, %Y')}."
            )
            return redirect('member_dashboard', member_id=record.member.id)
    else:
        form = BookIssueForm(initial=initial_data)

    return render(request, 'library/issue_book.html', {'form': form})


def return_book(request, record_id):
    """
    Book return workflow:
    - Calculates overdue fine based on return_date and due_date
    - Increments book.available_copies
    - Sets record.returned = True, records final fine amount
    """
    record = get_object_or_404(
        CirculationRecord.objects.select_related('book', 'member'),
        pk=record_id,
        returned=False
    )
    today = timezone.now().date()

    # Calculate initial overdue metrics
    initial_days_overdue = max(0, (today - record.due_date).days)
    initial_fine = Decimal(initial_days_overdue) * CirculationRecord.FINE_PER_DAY

    if request.method == 'POST':
        form = BookReturnForm(request.POST)
        if form.is_valid():
            return_date = form.cleaned_data['return_date']
            fine_input = form.cleaned_data.get('fine_amount')
            notes = form.cleaned_data.get('notes', '')

            # Server-side fine calculation validation
            computed_fine = record.compute_return_fine(return_date)
            # Use user-supplied fine if specified, else computed fine
            final_fine = fine_input if fine_input is not None else computed_fine

            record.return_date = return_date
            record.fine_amount = final_fine
            record.returned = True
            if notes:
                record.notes = (record.notes + " | " + notes).strip(" | ")
            record.save()

            # Increase available copies by 1
            book = record.book
            book.available_copies = min(book.total_copies, book.available_copies + 1)
            book.save()

            msg = f"'{book.title}' successfully returned by {record.member.name}."
            if final_fine > 0:
                msg += f" Overdue fine assessed: ${final_fine:.2f}."
            messages.success(request, msg)

            return redirect('member_dashboard', member_id=record.member.id)
    else:
        form = BookReturnForm(initial={
            'return_date': today,
            'fine_amount': initial_fine,
        })

    context = {
        'record': record,
        'form': form,
        'today': today,
        'initial_days_overdue': initial_days_overdue,
        'initial_fine': initial_fine,
        'fine_per_day': CirculationRecord.FINE_PER_DAY,
    }
    return render(request, 'library/return_book.html', context)


def member_list(request):
    """Member directory list with active loan counts and overdue badges."""
    members = Member.objects.annotate(
        total_loans=Count('circulation_records')
    ).all()

    query = request.GET.get('q', '')
    if query:
        members = members.filter(
            Q(name__icontains=query) |
            Q(member_id__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'members': members,
        'search_query': query,
    }
    return render(request, 'library/members.html', context)


def member_dashboard(request, member_id):
    """
    Member dashboard showing:
    - Currently borrowed books
    - Due dates and overdue alerts
    - Real-time estimated fines
    - Complete borrowing history
    """
    member = get_object_or_404(Member, pk=member_id)
    active_records = member.circulation_records.filter(returned=False).select_related('book').order_by('due_date')
    history_records = member.circulation_records.filter(returned=True).select_related('book').order_by('-return_date')

    today = timezone.now().date()
    total_active = active_records.count()
    overdue_count = 0
    total_accrued_fines = Decimal('0.00')

    # Add dynamic overdue calculations to active records
    for rec in active_records:
        if rec.due_date < today:
            overdue_count += 1
            total_accrued_fines += rec.current_estimated_fine

    total_past_fines = history_records.aggregate(total=Sum('fine_amount'))['total'] or Decimal('0.00')

    context = {
        'member': member,
        'active_records': active_records,
        'history_records': history_records,
        'today': today,
        'total_active': total_active,
        'overdue_count': overdue_count,
        'total_accrued_fines': total_accrued_fines,
        'total_past_fines': total_past_fines,
    }
    return render(request, 'library/member_dashboard.html', context)


def circulation_list(request):
    """Full circulation master list with filters for active, overdue, and returned."""
    status_filter = request.GET.get('status', 'all')
    records = CirculationRecord.objects.select_related('book', 'member').all()
    today = timezone.now().date()

    if status_filter == 'active':
        records = records.filter(returned=False)
    elif status_filter == 'overdue':
        records = records.filter(returned=False, due_date__lt=today)
    elif status_filter == 'returned':
        records = records.filter(returned=True)

    context = {
        'records': records,
        'status_filter': status_filter,
        'today': today,
        'total_active': CirculationRecord.objects.filter(returned=False).count(),
        'total_overdue': CirculationRecord.objects.filter(returned=False, due_date__lt=today).count(),
        'total_returned': CirculationRecord.objects.filter(returned=True).count(),
    }
    return render(request, 'library/circulation_list.html', context)


def calculator_view(request):
    """
    Interactive Due-Date and Fine Calculator.
    Allows patrons and librarians to project due dates and calculate overdue fines.
    """
    return render(request, 'library/calculator.html', {
        'fine_per_day': CirculationRecord.FINE_PER_DAY,
        'today': timezone.now().date(),
    })


def add_book(request):
    """View to register a new book into inventory."""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Book '{book.title}' successfully added to catalog.")
            return redirect('catalog')
    else:
        form = BookForm()
    return render(request, 'library/add_book.html', {'form': form})


def add_member(request):
    """View to register a new patron."""
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"Member '{member.name}' ({member.member_id}) registered successfully.")
            return redirect('member_dashboard', member_id=member.id)
    else:
        form = MemberForm()
    return render(request, 'library/add_member.html', {'form': form})


def add_author(request):
    """View to register a new author."""
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f"Author '{author.name}' created.")
            return redirect('add_book')
    else:
        form = AuthorForm()
    return render(request, 'library/add_author.html', {'form': form})


def seed_sample_data(request):
    """Populates realistic sample data to demonstrate all features."""
    from .seed_data import create_all_seed_data
    created = create_all_seed_data()
    messages.success(request, "Sample database seeded with rich catalog, authors, members, active loans, and overdue alerts!")
    return redirect('catalog')
