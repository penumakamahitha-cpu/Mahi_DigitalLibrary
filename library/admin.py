from django.contrib import admin
from .models import Author, Book, Member, CirculationRecord


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_bio', 'created_at')
    search_fields = ('name', 'biography')

    def short_bio(self, obj):
        return (obj.biography[:75] + '...') if len(obj.biography) > 75 else obj.biography
    short_bio.short_description = 'Biography'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'genre', 'available_copies', 'total_copies', 'is_in_stock')
    list_filter = ('genre', 'author')
    search_fields = ('title', 'isbn', 'author__name')

    def is_in_stock(self, obj):
        return obj.is_available
    is_in_stock.boolean = True
    is_in_stock.short_description = 'In Stock'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'name', 'email', 'phone', 'joined_date', 'active_loans')
    search_fields = ('member_id', 'name', 'email')
    list_filter = ('joined_date',)

    def active_loans(self, obj):
        return obj.active_loans_count
    active_loans.short_description = 'Active Loans'


@admin.register(CirculationRecord)
class CirculationRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'member', 'issue_date', 'due_date', 'return_date', 'returned', 'fine_amount', 'overdue_status')
    list_filter = ('returned', 'issue_date', 'due_date')
    search_fields = ('book__title', 'member__name', 'member__member_id', 'book__isbn')
    autocomplete_fields = ['book', 'member']

    def overdue_status(self, obj):
        return obj.is_overdue
    overdue_status.boolean = True
    overdue_status.short_description = 'Overdue'
