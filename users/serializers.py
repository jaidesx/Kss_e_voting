from rest_framework import serializers
from .models import Viewer

class ViewerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)  # optional

    class Meta:
        model = Viewer
        fields = ['id', 'username', 'email']  # Add other user fields if needed
