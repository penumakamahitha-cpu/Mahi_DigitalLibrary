from datetime import timedelta
from decimal import Decimal
from django import forms
from django.utils import timezone
from .models import Author, Book, Member, CirculationRecord


class BookIssueForm(forms.ModelForm):
    """Form to issue a book to a member."""
    class Meta:
        model = CirculationRecord
        fields = ['book', 'member', 'issue_date', 'due_date', 'notes']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select select2-book', 'id': 'id_book'}),
            'member': forms.Select(attrs={'class': 'form-select select2-member', 'id': 'id_member'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_issue_date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_due_date'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks or condition note'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show books with available copies for issue
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0)
        self.fields['book'].empty_label = "-- Select an Available Book --"
        self.fields['member'].empty_label = "-- Select a Registered Member --"
        
        # Set default dates
        today = timezone.now().date()
        if not self.initial.get('issue_date'):
            self.initial['issue_date'] = today
        if not self.initial.get('due_date'):
            self.initial['due_date'] = today + timedelta(days=14)

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        issue_date = cleaned_data.get('issue_date')
        due_date = cleaned_data.get('due_date')

        if book and book.available_copies <= 0:
            self.add_error('book', f"'{book.title}' currently has 0 copies available. It cannot be issued.")

        if issue_date and due_date and due_date < issue_date:
            self.add_error('due_date', "Due date cannot be before the issue date.")

        return cleaned_data


class BookReturnForm(forms.Form):
    """Form to process a book return with calculated fine."""
    return_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_return_date'}),
        initial=timezone.now().date
    )
    fine_amount = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50', 'id': 'id_fine_amount'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Condition upon return or fine notes'})
    )


class BookForm(forms.ModelForm):
    """Form to add or edit book catalog entries."""
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'genre', 'total_copies', 'available_copies', 'cover_url', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Clean Code'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 978-0132350884'}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/cover.jpg'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies')
        available = cleaned_data.get('available_copies')
        if total is not None and available is not None and available > total:
            self.add_error('available_copies', 'Available copies cannot be greater than total copies.')
        return cleaned_data


class MemberForm(forms.ModelForm):
    """Form to register or edit members."""
    class Meta:
        model = Member
        fields = ['name', 'member_id', 'email', 'phone', 'joined_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'member_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. LIB-1001'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'patron@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 555-0199'}),
            'joined_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get('joined_date'):
            self.initial['joined_date'] = timezone.now().date()


class AuthorForm(forms.ModelForm):
    """Form to add authors."""
    class Meta:
        model = Author
        fields = ['name', 'biography']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author Name'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Author Biography'}),
        }
