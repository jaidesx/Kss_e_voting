from django.urls import path
from .api_views import CandidateListAPIView, CandidateDetailAPIView

urlpatterns = [
    path('', CandidateListAPIView.as_view(), name='api_candidate_list'),
    path('<int:pk>/', CandidateDetailAPIView.as_view(), name='api_candidate_detail'),
]
