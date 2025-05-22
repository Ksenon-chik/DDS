from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Item, ExchangeProposal, Category
from .serializers import ItemCreateSerializer, ExchangeProposalSerializer
from .forms import ItemForm, ExchangeProposalForm
from .permissions import IsOwnerOrReadOnly


def index(request):
    # Поиск/фильтрация объявлений
    qs = Item.objects.filter(is_active=True)
    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    cat = request.GET.get('category')
    cond = request.GET.get('condition')
    if cat:
        qs = qs.filter(category_id=cat)
    if cond:
        qs = qs.filter(condition=cond)

    # Пагинация
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
    # Создание объявления
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            cat_name = form.cleaned_data['category_name']
            cond_text = form.cleaned_data['condition_text']
            category_obj, _ = Category.objects.get_or_create(name=cat_name)

            ad = form.save(commit=False)
            ad.owner = request.user
            ad.category = category_obj
            ad.condition = cond_text
            ad.save()
            return render(request, 'dds_app/create_success.html', {'ad': ad})
    else:
        form = ItemForm()

    return render(request, 'dds_app/ad_form.html', {'form': form, 'is_update': False})


def ad_update(request, pk):
    # Редактирование объявления — только владелец
    ad = get_object_or_404(Item, pk=pk, is_active=True)
    if request.user != ad.owner:
        messages.error(request, "Вы не можете редактировать это объявление.")
        return redirect('index')

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=ad)
        if form.is_valid():
            cat_name = form.cleaned_data['category_name']
            cond_text = form.cleaned_data['condition_text']
            category_obj, _ = Category.objects.get_or_create(name=cat_name)

            ad = form.save(commit=False)
            ad.category = category_obj
            ad.condition = cond_text
            ad.save()
            messages.success(request, "Объявление успешно обновлено.")
            return redirect('index')
    else:
        initial = {
            'category_name': ad.category.name if ad.category else '',
            'condition_text': ad.condition,
        }
        form = ItemForm(instance=ad, initial=initial)

    return render(request, 'dds_app/ad_form.html', {
        'form': form,
        'is_update': True,
    })


def ad_delete(request, pk):
    # Удаление объявления — только владелец
    ad = get_object_or_404(Item, pk=pk, is_active=True)
    if request.user != ad.owner:
        messages.error(request, "Вы не можете удалить это объявление.")
        return redirect('index')
    if request.method == 'POST':
        ad.delete()
        messages.success(request, "Объявление удалено.")
        return redirect('index')
    return render(request, 'dds_app/ad_confirm_delete.html', {'ad': ad})


def register(request):
    # Регистрация пользователя
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


@login_required
def proposal_create(request, receiver_pk):
    # Создание предложения обмена
    ad_receiver = get_object_or_404(Item, pk=receiver_pk, is_active=True)
    user_ads = Item.objects.filter(owner=request.user, is_active=True)

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        form.fields['ad_sender'].queryset = user_ads
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.status = 'pending'
            proposal.save()
            return render(request, 'dds_app/proposal_success.html', {'proposal': proposal})
    else:
        form = ExchangeProposalForm()
        form.fields['ad_sender'].queryset = user_ads

    return render(request, 'dds_app/proposal_form.html', {
        'form': form,
        'ad_receiver': ad_receiver
    })


@login_required
def proposal_list(request):
    # Просмотр и фильтрация предложений
    qs = ExchangeProposal.objects.filter(
        Q(ad_sender__owner=request.user) | Q(ad_receiver__owner=request.user)
    )
    sender = request.GET.get('sender')
    receiver = request.GET.get('receiver')
    status_filter = request.GET.get('status')
    if sender:
        qs = qs.filter(ad_sender_id=sender)
    if receiver:
        qs = qs.filter(ad_receiver_id=receiver)
    if status_filter:
        qs = qs.filter(status=status_filter)

    my_ads = Item.objects.filter(owner=request.user, is_active=True)
    return render(request, 'dds_app/proposal_list.html', {
        'proposals': qs,
        'my_ads': my_ads,
        'selected_sender': sender,
        'selected_receiver': receiver,
        'selected_status': status_filter,
    })


@login_required
@require_POST
def proposal_update_status(request, pk):
    # Обновление статуса предложения
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    if request.user not in [proposal.ad_sender.owner, proposal.ad_receiver.owner]:
        messages.error(request, "Нет прав менять этот статус.")
        return redirect('proposal_list')

    new_status = request.POST.get('status')
    if new_status in dict(ExchangeProposal.STATUS_CHOICES):
        proposal.status = new_status
        proposal.save()
        messages.success(request, f"Статус обновлен на «{proposal.get_status_display()}»")
    else:
        messages.error(request, "Неверный статус.")
    return redirect('proposal_list')


class ItemViewSet(viewsets.ModelViewSet):
    # REST API для объявлений
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
    # REST API для предложений обмена
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ad_sender', 'ad_receiver', 'status']
    search_fields = ['comment']

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
