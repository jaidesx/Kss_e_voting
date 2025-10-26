from rest_framework import serializers
from candidates.models import Candidate
from posts.models import Post
from voting.models import Voter, Vote


class CandidateSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    vote_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'post', 'post_title', '_class', 'photo', 
                  'stream', 'slogan', 'vote_count']
    
    def get_vote_count(self, obj):
        return Vote.objects.filter(candidate=obj).count()


class CandidateBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', '_class', 'photo', 'stream', 'slogan']


class CandidateResultSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Candidate
        fields = ['id', 'name', '_class', 'photo', 'stream', 'slogan', 'votes', 'percentage']
    
    def get_votes(self, obj):
        return Vote.objects.filter(candidate=obj).count()
    
    def get_percentage(self, obj):
        total_votes = Vote.objects.filter(post=obj.post).count()
        if total_votes == 0:
            return 0
        candidate_votes = Vote.objects.filter(candidate=obj).count()
        return round((candidate_votes / total_votes) * 100, 2)


