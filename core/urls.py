from django.contrib import admin
from django.urls import path, include
from voting.api_views import ElectionStatsAPIView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Candidates API
    path('api/candidates/', include('candidates.api_urls')),

    # Posts API
    path('api/posts/', include('posts.api_urls')),

    # Users/Viewers API
    path('api/users/', include('users.api_urls')),

    # Voting API (Voters + Votes + Election Stats)
    path('api/voting/', include('voting.api_urls')),
    path('api/voting/stats/', ElectionStatsAPIView.as_view(), name='api_election_stats'),
]
