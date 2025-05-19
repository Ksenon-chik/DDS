from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Item, ExchangeProposal, Category
from .serializers import ItemCreateSerializer, ExchangeProposalSerializer
from .forms import ItemForm, ExchangeProposalForm
from .permissions import IsOwnerOrReadOnly


def index(request):
    qs = Item.objects.filter(is_active=True)
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(description__icontains=q)
    cat = request.GET.get('category')
    cond = request.GET.get('condition')
    if cat:
        qs = qs.filter(category_id=cat)
    if cond:
        qs = qs.filter(condition=cond)
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    items_page = paginator.get_page(page)

    categories = Category.objects.all()
    return render(request, 'dds_app/index.html', {
        'items': items_page,
        'q': q,
        'selected_cat': cat,
        'selected_cond': cond,
        'categories': categories,
    })


def ad_create(request):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.owner = request.user
            ad.save()
            return render(request, 'dds_app/create_success.html', {'ad': ad})
    else:
        form = ItemForm()
    return render(request, 'dds_app/ad_form.html', {'form': form})


def proposal_create(request):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save()
            return render(request, 'dds_app/proposal_success.html', {'proposal': proposal})
    else:
        form = ExchangeProposalForm()
    return render(request, 'dds_app/proposal_form.html', {'form': form})


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(is_active=True)
    serializer_class = ItemCreateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    filterset_fields = ['category', 'condition']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'message': 'Объявление успешно создано', 'data': serializer.data},
            status=status.HTTP_201_CREATED
        )


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'message': 'Предложение отправлено', 'data': serializer.data},
            status=status.HTTP_201_CREATED
        )


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def ad_update(request, pk):
    ad = get_object_or_404(Item, pk=pk)
    if request.user != ad.owner:
        messages.error(request, "Вы не можете редактировать это объявление.")
        return redirect('index')
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, "Объявление обновлено.")
            return redirect('index')
    else:
        form = ItemForm(instance=ad)
    return render(request, 'dds_app/ad_form.html', {'form': form})


def ad_delete(request, pk):
    ad = get_object_or_404(Item, pk=pk)
    if request.user != ad.owner:
        messages.error(request, "Вы не можете удалить это объявление.")
        return redirect('index')
    if request.method == 'POST':
        ad.delete()
        messages.success(request, "Объявление удалено.")
        return redirect('index')
    return render(request, 'dds_app/ad_confirm_delete.html', {'ad': ad})
