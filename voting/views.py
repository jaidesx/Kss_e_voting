from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from posts.models import Post, Election
from voting.models import Voter, Vote
from .serializers import LiveResultsSerializer, VoteSerializer, BulkVoteSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def live_results(request):
    """
    Get live voting results grouped by position for a specific or active election.
    """
    election_id = request.query_params.get('election_id')
    
    if election_id:
        try:
            election = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Election not found.'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        election = Election.objects.filter(is_active=True).first()
        if not election:
            election = Election.objects.order_by('-created_at').first()
            
    if not election:
        return Response({
            'success': True,
            'data': {
                'positions': [],
                'statistics': {
                    'total_voters': 0,
                    'voted_count': 0,
                    'voter_turnout_percentage': 0
                }
            }
        }, status=status.HTTP_200_OK)

    posts = Post.objects.filter(election=election).prefetch_related('candidates')
    serializer = LiveResultsSerializer(posts, many=True)
    
    total_voters = Voter.objects.count()
    voted_count = Voter.objects.filter(vote__post__election=election).distinct().count()
    
    return Response({
        'success': True,
        'data': {
            'election': {
                'id': election.id,
                'title': election.title,
                'is_active': election.is_active,
                'is_demo': election.is_demo,
            },
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
    Get current voter's voting status for the active election
    """
    voter = request.user
    active_election = Election.objects.filter(is_active=True).first()
    
    if not active_election:
        return Response({
            'success': True,
            'data': {
                'voter': {
                    'id': voter.id,
                    'voter_no': voter.voter_no,
                    'name': voter.full_name,
                    'house': voter.house,
                },
                'active_election': None,
                'eligible_positions': [],
                'voted_positions': [],
                'votes_cast': 0
            }
        }, status=status.HTTP_200_OK)
        
    voted_positions = Vote.objects.filter(voter=voter, post__election=active_election).values_list('post__title', flat=True).distinct()
    
    # Get positions this voter is eligible to vote for in the active election
    all_posts = Post.objects.filter(election=active_election).prefetch_related('eligible_houses')
    eligible_positions = [
        {'id': post.id, 'title': post.title}
        for post in all_posts
        if post.is_voter_eligible(voter)
    ]
    
    return Response({
        'success': True,
        'data': {
            'voter': {
                'id': voter.id,
                'voter_no': voter.voter_no,
                'name': voter.full_name,
                'house': voter.house,
            },
            'active_election': {
                'id': active_election.id,
                'title': active_election.title,
                'is_demo': active_election.is_demo
            },
            'eligible_positions': eligible_positions,
            'voted_positions': list(voted_positions),
            'votes_cast': Vote.objects.filter(voter=voter, post__election=active_election).count()
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

