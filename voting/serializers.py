from rest_framework import serializers
from candidates.serializers import CandidateResultSerializer

from posts.models import Post
from voting.models import Vote

class LiveResultsSerializer(serializers.ModelSerializer):
    candidates = CandidateResultSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'total_votes', 'candidates']
    
    def get_total_votes(self, obj):
        return Vote.objects.filter(post=obj).count()


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['post', 'candidate']
    
    def validate(self, data):
        voter = self.context['request'].user
        post = data['post']
        candidate = data['candidate']
        
        # Check if voter already voted for this post
        if Vote.objects.filter(voter=voter, post=post).exists():
            raise serializers.ValidationError("You have already voted for this position.")
        
        # Check if candidate belongs to the post
        if candidate.post != post:
            raise serializers.ValidationError("Candidate does not belong to this position.")
        
        return data
    
    def create(self, validated_data):
        voter = self.context['request'].user
        vote = Vote.objects.create(voter=voter, **validated_data)
        
        # Update voter's has_voted status
        if not voter.has_voted:
            voter.has_voted = True
            voter.save()
        
        return vote


class BulkVoteSerializer(serializers.Serializer):
    votes = VoteSerializer(many=True)
    
    def validate_votes(self, votes_data):
        if not votes_data:
            raise serializers.ValidationError("At least one vote is required.")
        
        # Check for duplicate posts in the same request
        post_ids = [vote['post'].id for vote in votes_data]
        if len(post_ids) != len(set(post_ids)):
            raise serializers.ValidationError("Cannot vote for the same position multiple times.")
        
        return votes_data
    
    def validate(self, data):
        voter = self.context['request'].user
        votes_data = data['votes']
        
        # Validate each vote
        for vote_data in votes_data:
            post = vote_data['post']
            candidate = vote_data['candidate']
            
            # Check if voter already voted for this post
            if Vote.objects.filter(voter=voter, post=post).exists():
                raise serializers.ValidationError(
                    f"You have already voted for position: {post.title}"
                )
            
            # Check if candidate belongs to the post
            if candidate.post != post:
                raise serializers.ValidationError(
                    f"Candidate {candidate.name} does not belong to position: {post.title}"
                )
        
        return data
    
    def create(self, validated_data):
        voter = self.context['request'].user
        votes_data = validated_data['votes']
        
        # Create all votes
        created_votes = []
        for vote_data in votes_data:
            vote = Vote.objects.create(
                voter=voter,
                post=vote_data['post'],
                candidate=vote_data['candidate']
            )
            created_votes.append(vote)
        
        # Update voter's has_voted status
        if not voter.has_voted:
            voter.has_voted = True
            voter.save()
        
        return created_votes
