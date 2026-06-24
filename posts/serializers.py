from rest_framework import serializers
from candidates.serializers import CandidateBasicSerializer

from .models import Post, Election


class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['id', 'title', 'description', 'is_active', 'is_demo', 'created_at']


class PostWithCandidatesSerializer(serializers.ModelSerializer):
    candidates = CandidateBasicSerializer(many=True, read_only=True)
    candidate_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'election', 'title', 'description', 'required_selections', 'candidate_count', 'candidates']
    
    def get_candidate_count(self, obj):
        return obj.candidates.count()

