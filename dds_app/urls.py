from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    index,
    ad_create,
    ad_update,
    ad_delete,
    proposal_create,
    proposal_list,
    proposal_update_status,
    ItemViewSet,
    ExchangeProposalViewSet
)

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='items')
router.register(r'proposals', ExchangeProposalViewSet, basename='proposals')

urlpatterns = [
    path('', index, name='index'),
    path('create/', ad_create, name='ad_create'),
    path('edit/<int:pk>/', ad_update, name='ad_update'),
    path('delete/<int:pk>/', ad_delete, name='ad_delete'),

    path('proposal/create/<int:receiver_pk>/', proposal_create, name='proposal_create'),
    path('proposal/', proposal_list, name='proposal_list'),
    # изменение статуса предложения
    path('proposal/<int:pk>/status/', proposal_update_status, name='proposal_update_status'),

    path('api/', include(router.urls)),
]
