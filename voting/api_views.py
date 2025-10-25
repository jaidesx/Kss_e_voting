from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from candidates.models import Candidate
from voting.models import Vote, Voter
from .serializers import ElectionStatsSerializer, CandidateResultSerializer

class ElectionStatsAPIView(APIView):
    """
    Returns JSON with total voters, total votes, and candidate results
    """
    def get(self, request):
        total_voters = Voter.objects.count()
        total_votes = Vote.objects.count()

        candidates = Candidate.objects.annotate(vote_count=Count('vote'))
        results = []

        for candidate in candidates:
            vote_count = candidate.vote_count
            percentage = (vote_count / total_votes * 100) if total_votes else 0
            results.append({
                "name": candidate.name,
                "post": candidate.post.title,
                "votes": vote_count,
                "percentage": round(percentage, 2)
            })

        data = {
            "total_voters": total_voters,
            "total_votes": total_votes,
            "results": results
        }

        serializer = ElectionStatsSerializer(data)
        return Response(serializer.data)
