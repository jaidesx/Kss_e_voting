from django.urls import path
from .api_views import ViewerListAPIView, ViewerDetailAPIView

urlpatterns = [
    path('', ViewerListAPIView.as_view(), name='api_user_list'),
    path('<int:pk>/', ViewerDetailAPIView.as_view(), name='api_user_detail'),
]
