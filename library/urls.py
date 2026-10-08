from django.urls import path
from . import views

urlpatterns = [
    # Book catalog & details
    path('', views.book_catalog, name='catalog'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/add/', views.add_book, name='add_book'),
    path('authors/add/', views.add_author, name='add_author'),

    # Circulation workflows
    path('issue/', views.issue_book, name='issue_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('circulation/', views.circulation_list, name='circulation_list'),

    # Members & Patron Dashboard
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/<int:member_id>/', views.member_dashboard, name='member_dashboard'),

    # Due-Date and Fine Tools
    path('calculator/', views.calculator_view, name='calculator'),
    path('seed-data/', views.seed_sample_data, name='seed_sample_data'),
]
