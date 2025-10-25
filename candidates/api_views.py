from rest_framework import generics
from .models import Candidate
from .serializers import CandidateSerializer

class CandidateListAPIView(generics.ListAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer

class CandidateDetailAPIView(generics.RetrieveAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
