from django.urls import path
from .views import (
    # Transactions
    TransactionListView,
    TransactionCreateView,
    TransactionUpdateView,
    TransactionDeleteView,
    load_categories,
    load_subcategories,
    # Status
    StatusCreateView,
    StatusUpdateView,
    # Type
    TypeCreateView,
    TypeUpdateView,
    # Category
    CategoryCreateView,
    CategoryUpdateView,
    # Subcategory
    SubcategoryCreateView,
    SubcategoryUpdateView,
)

urlpatterns = [
    # Transaction CRUD
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('transaction/add/', TransactionCreateView.as_view(), name='transaction-add'),
    path('transaction/<int:pk>/edit/', TransactionUpdateView.as_view(), name='transaction-update'),
    path('transaction/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction-delete'),

    # AJAX for dynamic selects
    path('ajax/load-categories/', load_categories, name='ajax_load_categories'),
    path('ajax/load-subcategories/', load_subcategories, name='ajax_load_subcategories'),

    # Status management
    path('status/add/', StatusCreateView.as_view(), name='status-add'),
    path('status/<int:pk>/edit/', StatusUpdateView.as_view(), name='status-edit'),

    # Type management
    path('type/add/', TypeCreateView.as_view(), name='type-add'),
    path('type/<int:pk>/edit/', TypeUpdateView.as_view(), name='type-edit'),

    # Category management
    path('category/add/', CategoryCreateView.as_view(), name='category-add'),
    path('category/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category-edit'),

    # Subcategory management
    path('subcategory/add/', SubcategoryCreateView.as_view(), name='subcategory-add'),
    path('subcategory/<int:pk>/edit/', SubcategoryUpdateView.as_view(), name='subcategory-edit'),
]
