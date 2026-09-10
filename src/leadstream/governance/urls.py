from django.urls import path

from .views import ApplyRetentionView, SuppressionCollectionView

urlpatterns = [
    path("supressoes/", SuppressionCollectionView.as_view(), name="suppression-list"),
    path("retencao/aplicar/", ApplyRetentionView.as_view(), name="retention-apply"),
]
