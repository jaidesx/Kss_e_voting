from rest_framework import generics
from .models import Viewer
from .serializers import ViewerSerializer

# Read-only API views
class ViewerListAPIView(generics.ListAPIView):
    queryset = Viewer.objects.select_related('user').all()
    serializer_class = ViewerSerializer

class ViewerDetailAPIView(generics.RetrieveAPIView):
    queryset = Viewer.objects.select_related('user').all()
    serializer_class = ViewerSerializer
