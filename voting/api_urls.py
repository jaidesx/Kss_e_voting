from django.urls import path
from .api_views import ElectionStatsAPIView

urlpatterns = [
    path('stats/', ElectionStatsAPIView.as_view(), name='api_election_stats'),
    # You can add voter/vote read-only APIs here later
]
