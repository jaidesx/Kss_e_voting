from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.db import IntegrityError
from candidates.models import Candidate
from posts.models import Post
from voting.models import Vote, Voter
from .serializers import ElectionStatsSerializer, CandidateResultSerializer, VoteSerializer

class VoteAPIView(APIView):
    """
    Handle voting operations
    """
    def post(self, request):
        serializer = VoteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                vote = serializer.save()
                return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"error": "You have already voted for this post"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
