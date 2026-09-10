from django.urls import path

from .views import BatchFinancialSummaryView, PriceBookCollectionView

urlpatterns = [
    path("precos/", PriceBookCollectionView.as_view(), name="price-book-list"),
    path(
        "lotes/<uuid:batch_id>/financeiro/",
        BatchFinancialSummaryView.as_view(),
        name="batch-financial-summary",
    ),
]
