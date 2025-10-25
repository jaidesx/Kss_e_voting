from rest_framework import serializers

class CandidateResultSerializer(serializers.Serializer):
    name = serializers.CharField()
    post = serializers.CharField()
    votes = serializers.IntegerField()
    percentage = serializers.FloatField()

class ElectionStatsSerializer(serializers.Serializer):
    total_voters = serializers.IntegerField()
    total_votes = serializers.IntegerField()
    results = CandidateResultSerializer(many=True)
