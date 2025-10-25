from rest_framework import serializers
from .models import Vote

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['voter', 'post', 'candidate', 'timestamp']

class CandidateResultSerializer(serializers.Serializer):
    name = serializers.CharField()
    post = serializers.CharField()
    votes = serializers.IntegerField()
    percentage = serializers.FloatField()

class ElectionStatsSerializer(serializers.Serializer):
    total_voters = serializers.IntegerField()
    total_votes = serializers.IntegerField()
    results = CandidateResultSerializer(many=True)
