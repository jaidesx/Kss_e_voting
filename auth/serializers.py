from rest_framework import serializers
from django.contrib.auth import authenticate

from voting.models import Voter
from .models import Viewer

class VoterLoginSerializer(serializers.Serializer):
    voter_no = serializers.CharField(max_length=50)
    
    def validate_voter_no(self, value):
        try:
            voter = Voter.objects.get(voter_no=value)
        except Voter.DoesNotExist:
            raise serializers.ValidationError("Invalid voter number.")
        return value


class ViewerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            # Authenticate user with email
            user = authenticate(username=email, password=password)
            
            if not user:
                # Try authenticating with email field if username doesn't work
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                
                # Check if user is a viewer
                try:
                    viewer = Viewer.objects.get(user=user)
                    data['user'] = user
                    data['viewer'] = viewer
                except Viewer.DoesNotExist:
                    raise serializers.ValidationError("This user is not authorized as a viewer.")
            else:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            raise serializers.ValidationError("Must include email and password.")
        
        return data


class ViewerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = Viewer
        fields = ['id', 'username', 'email', 'first_name', 'last_name']