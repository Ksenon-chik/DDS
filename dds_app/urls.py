from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    index,
    ad_create,
    proposal_create,
    ad_update,
    ad_delete,
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
    path('proposal/', proposal_create, name='proposal_create'),  # здесь
    path('api/', include(router.urls)),
]
