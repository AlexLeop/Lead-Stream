from django.urls import path

from .views import (
    CompanyCollectionView,
    ContactCollectionView,
    EstablishmentCollectionView,
    PersonCollectionView,
    RelationshipCollectionView,
    SocialProfileCollectionView,
)

urlpatterns = [
    path("empresas/", CompanyCollectionView.as_view(), name="company-list"),
    path("estabelecimentos/", EstablishmentCollectionView.as_view(), name="establishment-list"),
    path("pessoas/", PersonCollectionView.as_view(), name="person-list"),
    path("vinculos/", RelationshipCollectionView.as_view(), name="relationship-list"),
    path("contatos/", ContactCollectionView.as_view(), name="contact-list"),
    path("perfis-sociais/", SocialProfileCollectionView.as_view(), name="social-profile-list"),
]
