from django.urls import path
from .views import (
    OrganizationListCreateView, OrganizationDetailView,
    OrganizationMembershipListView, join_organization, leave_organization
)

urlpatterns = [
    path('', OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('<uuid:pk>/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('<uuid:organization_id>/members/', OrganizationMembershipListView.as_view(), name='organization-members'),
    path('<uuid:organization_id>/join/', join_organization, name='join-organization'),
    path('<uuid:organization_id>/leave/', leave_organization, name='leave-organization'),
]
