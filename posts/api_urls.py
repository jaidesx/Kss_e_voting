from django.urls import path
from .api_views import PostListAPIView, PostDetailAPIView

urlpatterns = [
    path('', PostListAPIView.as_view(), name='api_post_list'),
    path('<int:pk>/', PostDetailAPIView.as_view(), name='api_post_detail'),
]
