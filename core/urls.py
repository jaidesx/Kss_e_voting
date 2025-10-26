from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from candidates.api_views import CandidateViewSet
from posts.api_views import PostViewSet

from auth.api_views import voter_login, viewer_login
from voting.api_views import live_results, cast_bulk_votes, voter_status

router = DefaultRouter()
router.register(r'api/candidates', CandidateViewSet, basename='candidate')
router.register(r'api/positions', PostViewSet, basename='position')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api/auth/voter/login/', voter_login, name='voter-login'),
    path('api/auth/viewer/login/', viewer_login, name='viewer-login'),
    path('api/results/live/', live_results, name='live-results'),
    path('api/vote/cast/', cast_bulk_votes, name='cast-vote'),
    path('api/voter/status/', voter_status, name='voter-status'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
