from django.urls import path

from .views import (
    BatchChunksView,
    BatchCollectionView,
    BatchDetailView,
    BatchItemsView,
    CancelBatchView,
    PauseBatchView,
    ResumeBatchView,
)

urlpatterns = [
    path("", BatchCollectionView.as_view(), name="batch-list"),
    path("<uuid:batch_id>/", BatchDetailView.as_view(), name="batch-detail"),
    path("<uuid:batch_id>/itens/", BatchItemsView.as_view(), name="batch-items"),
    path("<uuid:batch_id>/chunks/", BatchChunksView.as_view(), name="batch-chunks"),
    path("<uuid:batch_id>/pausar/", PauseBatchView.as_view(), name="batch-pause"),
    path("<uuid:batch_id>/retomar/", ResumeBatchView.as_view(), name="batch-resume"),
    path("<uuid:batch_id>/cancelar/", CancelBatchView.as_view(), name="batch-cancel"),
]
