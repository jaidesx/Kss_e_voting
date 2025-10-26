from rest_framework import serializers
from candidates.serializers import CandidateBasicSerializer

from .models import Post

class PostWithCandidatesSerializer(serializers.ModelSerializer):
    candidates = CandidateBasicSerializer(many=True, read_only=True)
    candidate_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'candidate_count', 'candidates']
    
    def get_candidate_count(self, obj):
        return obj.candidates.count()
