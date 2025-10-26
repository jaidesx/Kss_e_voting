from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from voting.models import Voter


class VoterJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for Voter model
    """
    def get_user(self, validated_token):
        try:
            voter_id = validated_token.get('voter_id')
            if voter_id is None:
                raise InvalidToken('Token contained no recognizable voter identification')
            
            voter = Voter.objects.get(id=voter_id)
            return voter
            
        except Voter.DoesNotExist:
            raise InvalidToken('Voter not found')
