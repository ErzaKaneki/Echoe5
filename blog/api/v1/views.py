from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from blog.models import Post
from blog.serializers import PostSerializer
from users.authentication import CustomJWTAuthentication # Changed from blog.authentication
import logging

logger = logging.getLogger(__name__)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Post.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(author=self.request.user)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        logger.info(f"Post created by user {self.request.user.username}")