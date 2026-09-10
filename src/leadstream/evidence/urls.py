from django.urls import path

from .views import (
    CanonicalDecisionCollectionView,
    CanonicalizeView,
    ConflictCollectionView,
    EvidenceCollectionView,
    ObservationCollectionView,
    PurposeCollectionView,
    RetentionPolicyCollectionView,
    SourceCollectionView,
    SourceRecordCollectionView,
)

urlpatterns = [
    path("finalidades/", PurposeCollectionView.as_view(), name="purpose-list"),
    path("retencao/politicas/", RetentionPolicyCollectionView.as_view(), name="retention-list"),
    path("fontes/", SourceCollectionView.as_view(), name="source-list"),
    path("fontes/registros/", SourceRecordCollectionView.as_view(), name="source-record-list"),
    path("evidencias/", EvidenceCollectionView.as_view(), name="evidence-list"),
    path("observacoes/", ObservationCollectionView.as_view(), name="observation-list"),
    path("canonizar/", CanonicalizeView.as_view(), name="canonicalize"),
    path("decisoes-canonicas/", CanonicalDecisionCollectionView.as_view(), name="decision-list"),
    path("conflitos/", ConflictCollectionView.as_view(), name="conflict-list"),
]
