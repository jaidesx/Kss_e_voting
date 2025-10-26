from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from posts.models import Post
from .serializers import PostWithCandidatesSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all positions with candidate count
    """
    queryset = Post.objects.all().prefetch_related('candidates')
    serializer_class = PostWithCandidatesSerializer
    permission_classes = [AllowAny]

