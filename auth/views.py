from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from voting.models import Voter, Vote
from .serializers import VoterLoginSerializer,ViewerLoginSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def voter_login(request):
    """
    Voter login with voter_no
    Returns JWT token and voting status
    """
    serializer = VoterLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        voter = serializer.validated_data['voter']
        
        # Check if voter has already voted for all eligible positions
        from posts.models import Post, Election
        from django.db.models import Count

        active_election = Election.objects.filter(is_active=True).first()
        if active_election:
            posts = Post.objects.filter(election=active_election).prefetch_related('eligible_houses')
            eligible_posts = [post for post in posts if post.is_voter_eligible(voter)]
            if eligible_posts:
                votes_by_post = {
                    item['post']: item['vote_count']
                    for item in Vote.objects.filter(voter=voter, post__in=eligible_posts)
                                           .values('post')
                                           .annotate(vote_count=Count('id'))
                }
                has_voted_all = all(
                    votes_by_post.get(post.id, 0) >= (post.required_selections or 1)
                    for post in eligible_posts
                )
                if has_voted_all:
                    return Response({
                        'success': False,
                        'message': 'You have already voted.'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate JWT token
        refresh = RefreshToken()
        refresh['voter_id'] = voter.id
        refresh['voter_no'] = voter.voter_no
        refresh['name'] = voter.full_name
        
        has_voted = Vote.objects.filter(voter=voter).exists()
        
        return Response({
            'success': True,
            'message': 'Login successful' if not has_voted else 'You have already voted',
            'data': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'voter': {
                    'id': voter.id,
                    'voter_no': voter.voter_no,
                    'name': voter.full_name,
                    'house': voter.house,
                    'has_voted': has_voted
                }
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Invalid voter number.',
        'errors': serializer.errors
    }, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['POST'])
@permission_classes([AllowAny])
def viewer_login(request):
    """
    Viewer login with email and password
    Returns JWT token for viewing results
    """
    serializer = ViewerLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        viewer = serializer.validated_data['viewer']
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        refresh['viewer_id'] = viewer.id
        refresh['user_type'] = 'viewer'
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'viewer': {
                    'id': viewer.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': 'viewer'
                }
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Login failed',
        'errors': serializer.errors
    }, status=status.HTTP_401_UNAUTHORIZED)
