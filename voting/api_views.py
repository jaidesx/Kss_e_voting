from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from posts.models import Post
from voting.models import Voter, Vote
from .serializers import LiveResultsSerializer,VoteSerializer, BulkVoteSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def live_results(request):
    """
    Get live voting results grouped by position
    """
    posts = Post.objects.all().prefetch_related('candidates')
    serializer = LiveResultsSerializer(posts, many=True)
    
    total_voters = Voter.objects.count()
    voted_count = Voter.objects.filter(has_voted=True).count()
    
    return Response({
        'success': True,
        'data': {
            'positions': serializer.data,
            'statistics': {
                'total_voters': total_voters,
                'voted_count': voted_count,
                'voter_turnout_percentage': round((voted_count / total_voters * 100), 2) if total_voters > 0 else 0
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_vote(request):
    """
    Cast a vote for a candidate
    Voter must be authenticated via JWT
    """
    voter = request.user
    
    serializer = VoteSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Vote cast successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Failed to cast vote',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def voter_status(request):
    """
    Get current voter's voting status
    """
    voter = request.user
    voted_positions = Vote.objects.filter(voter=voter).values_list('post__title', flat=True)
    
    return Response({
        'success': True,
        'data': {
            'voter': {
                'id': voter.id,
                'voter_no': voter.voter_no,
                'name': voter.name,
                'house': voter.house,
                'has_voted': voter.has_voted
            },
            'voted_positions': list(voted_positions),
            'votes_cast': Vote.objects.filter(voter=voter).count()
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_bulk_votes(request):
    """
    Cast votes for multiple positions at once
    Voter must be authenticated via JWT
    
    Expected request body format:
    {
        "votes": [
            {"post": 1, "candidate": 3},
            {"post": 2, "candidate": 5},
            {"post": 3, "candidate": 7}
        ]
    }
    """
    voter = request.user
    
    serializer = BulkVoteSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        created_votes = serializer.save()
        return Response({
            'success': True,
            'message': f'{len(created_votes)} votes cast successfully',
            'votes_count': len(created_votes)
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Failed to cast votes',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

