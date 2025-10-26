from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from candidates.models import Candidate
from .serializers import (
    CandidateSerializer
)


class CandidateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all candidates
    """
    queryset = Candidate.objects.all().select_related('post')
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]
