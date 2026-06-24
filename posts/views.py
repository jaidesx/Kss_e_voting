from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.db.models import Q

from posts.models import Post, Election
from voting.models import Voter
from .serializers import PostWithCandidatesSerializer, ElectionSerializer


class ElectionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all elections
    """
    queryset = Election.objects.all().order_by('-created_at')
    serializer_class = ElectionSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List positions with candidate count.
    Defaults to the active election. Filters by ?election_id= if provided.
    Filters positions by voter house eligibility if requested by a Voter.
    """
    serializer_class = PostWithCandidatesSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Post.objects.all().prefetch_related('candidates')
        election_id = self.request.query_params.get('election_id')
        if election_id:
            queryset = queryset.filter(election_id=election_id)
        else:
            active_election = Election.objects.filter(is_active=True).first()
            if active_election:
                queryset = queryset.filter(election=active_election)
            else:
                queryset = queryset.none()

        # Filter by voter's house eligibility rules if the user is authenticated as a Voter
        user = self.request.user
        if user and user.is_authenticated and isinstance(user, Voter):
            if user.house:
                queryset = queryset.filter(
                    Q(eligible_houses__isnull=True) | Q(eligible_houses__house=user.house)
                ).distinct()
            else:
                queryset = queryset.filter(eligible_houses__isnull=True).distinct()

        return queryset



