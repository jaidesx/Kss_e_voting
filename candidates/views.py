from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from candidates.models import Candidate
from posts.models import Election
from .serializers import (
    CandidateSerializer
)


class CandidateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List candidates.
    Defaults to active election candidates. Filters by ?election_id= if provided.
    """
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Candidate.objects.all().select_related('post')
        election_id = self.request.query_params.get('election_id')
        if election_id:
            queryset = queryset.filter(post__election_id=election_id)
        else:
            active_election = Election.objects.filter(is_active=True).first()
            if active_election:
                queryset = queryset.filter(post__election=active_election)
            else:
                queryset = queryset.none()
        return queryset

