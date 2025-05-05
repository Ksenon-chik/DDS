# dds_app/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models.deletion import ProtectedError

from .models import Transaction, Status, Type, Category, Subcategory
from .forms import TransactionForm

# --- Transactions CRUD ---
class TransactionListView(ListView):
    model = Transaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = Q()
        df = self.request.GET.get('date_from')
        dt = self.request.GET.get('date_to')
        st = self.request.GET.get('status')
        tp = self.request.GET.get('type')
        cat = self.request.GET.get('category')
        sub = self.request.GET.get('subcategory')
        if df: q &= Q(date__gte=parse_date(df))
        if dt: q &= Q(date__lte=parse_date(dt))
        if st: q &= Q(status_id=st)
        if tp: q &= Q(type_id=tp)
        if cat: q &= Q(category_id=cat)
        if sub: q &= Q(subcategory_id=sub)
        return qs.filter(q)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statuses'] = Status.objects.all()
        ctx['types'] = Type.objects.all()
        ctx['categories'] = Category.objects.all()
        ctx['subcategories'] = Subcategory.objects.all()
        return ctx

class TransactionCreateView(CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction-list')

class TransactionUpdateView(UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'transaction_form.html'
    success_url = reverse_lazy('transaction-list')

class TransactionDeleteView(DeleteView):
    model = Transaction
    template_name = 'transaction_confirm_delete.html'
    success_url = reverse_lazy('transaction-list')

# --- AJAX handlers ---
def load_categories(request):
    t = request.GET.get('type')
    qs = Category.objects.filter(type_id=t).order_by('name')
    return JsonResponse(list(qs.values('id', 'name')), safe=False)

def load_subcategories(request):
    c = request.GET.get('category')
    qs = Subcategory.objects.filter(category_id=c).order_by('name')
    return JsonResponse(list(qs.values('id', 'name')), safe=False)

# --- Reference management (Status, Type, Category, Subcategory) ---

class StatusCreateView(CreateView):
    model = Status
    fields = ['name']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')

class StatusUpdateView(UpdateView):
    model = Status
    fields = ['name']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')

class TypeCreateView(CreateView):
    model = Type
    fields = ['name']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')

class TypeUpdateView(UpdateView):
    model = Type
    fields = ['name']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')

class CategoryCreateView(CreateView):
    model = Category
    fields = ['name', 'type']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')

class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name', 'type']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')

class SubcategoryCreateView(CreateView):
    model = Subcategory
    fields = ['name', 'category']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')

class SubcategoryUpdateView(UpdateView):
    model = Subcategory
    fields = ['name', 'category']
    template_name = 'simple_form.html'
    success_url = reverse_lazy('transaction-add')
