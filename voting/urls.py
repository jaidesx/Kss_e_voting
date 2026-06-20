from django.urls import path
from .api_views import ElectionStatsAPIView, VoteAPIView

urlpatterns = [
    path('vote/', VoteAPIView.as_view(), name='api_vote'),
    path('stats/', ElectionStatsAPIView.as_view(), name='api_election_stats'),
    # You can add voter/vote read-only APIs here later
]
