from rest_framework import serializers
from candidates.serializers import CandidateResultSerializer

from posts.models import Post, Election
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
        
        # Check active election
        active_election = Election.objects.filter(is_active=True).first()
        if not active_election:
            raise serializers.ValidationError("There is no active election at the moment.")
        if post.election != active_election:
            raise serializers.ValidationError("This position is not part of the active election.")
        
        # Check if voter is eligible for this post
        if not post.is_voter_eligible(voter):
            raise serializers.ValidationError("You are not eligible to vote for this position.")
        
        # Enforce required_selections if voting via the single vote endpoint
        if not self.parent and post.required_selections != 1:
            raise serializers.ValidationError(
                f"Position {post.title} requires exactly {post.required_selections} selections. Please use the bulk voting endpoint."
            )
        
        # Check if voter already voted for this post in DB
        if Vote.objects.filter(voter=voter, post=post).exists():
            raise serializers.ValidationError("You have already voted for this position.")
        
        # Check if candidate belongs to the post
        if candidate.post != post:
            raise serializers.ValidationError("Candidate does not belong to this position.")
        
        return data
    
    def create(self, validated_data):
        voter = self.context['request'].user
        vote = Vote.objects.create(voter=voter, **validated_data)
        return vote
 
 
class BulkVoteSerializer(serializers.Serializer):
    votes = VoteSerializer(many=True)
    
    def validate_votes(self, votes_data):
        if not votes_data:
            raise serializers.ValidationError("At least one vote is required.")
        return votes_data
    
    def validate(self, data):
        voter = self.context['request'].user
        votes_data = data['votes']
        
        active_election = Election.objects.filter(is_active=True).first()
        if not active_election:
            raise serializers.ValidationError("There is no active election at the moment.")
        
        # Group votes by post to validate quantities
        post_selections = {}
        for vote_data in votes_data:
            post = vote_data['post']
            candidate = vote_data['candidate']
            post_selections.setdefault(post, []).append(candidate.id)
            
            # Verify basic election matching
            if post.election != active_election:
                raise serializers.ValidationError(
                    f"Position {post.title} is not part of the active election."
                )
            
            # Check voter eligibility for this post
            if not post.is_voter_eligible(voter):
                raise serializers.ValidationError(
                    f"You are not eligible to vote for position: {post.title}"
                )
            
            # Check if candidate belongs to the post
            if candidate.post != post:
                raise serializers.ValidationError(
                    f"Candidate {candidate.name} does not belong to position: {post.title}"
                )
        
        # Validate grouped selections per post
        for post, candidate_ids in post_selections.items():
            # Check if selection count matches required_selections
            if len(candidate_ids) != post.required_selections:
                raise serializers.ValidationError(
                    f"You must select exactly {post.required_selections} candidate(s) for position: {post.title}."
                )
            # Check for duplicate candidates in the same post
            if len(candidate_ids) != len(set(candidate_ids)):
                raise serializers.ValidationError(
                    f"Cannot vote for the same candidate multiple times for position: {post.title}."
                )
            # Check if voter already voted for this post in DB
            if Vote.objects.filter(voter=voter, post=post).exists():
                raise serializers.ValidationError(
                    f"You have already voted for position: {post.title}"
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
        
        return created_votes
