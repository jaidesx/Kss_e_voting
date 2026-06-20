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
    Voter login with voter_no and PIN
    Returns JWT token and voting status
    """
    serializer = VoterLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        voter = serializer.validated_data['voter']
        
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
        'message': 'Invalid voter number or PIN',
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
