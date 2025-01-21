from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from blog.models import Post
from blog.serializers import PostSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)