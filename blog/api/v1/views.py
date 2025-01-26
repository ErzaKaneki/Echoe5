from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from blog.models import Post
from blog.serializers import PostSerializer
from users.authentication import CustomJWTAuthentication
import logging

logger = logging.getLogger(__name__)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Post.objects.all().order_by('-date_posted')
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'data': serializer.data,
                'message': 'Posts retrieved successfully'
            })
        except Exception as e:
            logger.error(f"Error retrieving posts: {str(e)}")
            return Response({
                'success': False,
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Error retrieving posts'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(author=request.user)
            return Response({
                'success': True,
                'status': status.HTTP_201_CREATED,
                'data': serializer.data,
                'message': 'Post created successfully'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"Error retrieving post: {str(e)}")
            return Response({
                'success': False,
                'status': status.HTTP_404_NOT_FOUND,
                'message': 'Post not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check permissions first
        if instance.author != request.user and not request.user.is_staff:
            return Response({
                'success': False,
                'status': status.HTTP_403_FORBIDDEN,
                'message': 'You do not have permission to modify this post'
            }, status=status.HTTP_403_FORBIDDEN)
            
        try:
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'success': True,
                'status': status.HTTP_200_OK,
                'data': serializer.data,
                'message': 'Post updated successfully'
            })
        except Exception as e:
            logger.error(f"Error updating post: {str(e)}")
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.author != request.user and not request.user.is_staff:
                return Response({
                    'success': False,
                    'status': status.HTTP_403_FORBIDDEN,
                    'message': 'You do not have permission to delete this post'
                }, status=status.HTTP_403_FORBIDDEN)
                
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting post: {str(e)}")
            return Response({
                'success': False,
                'status': status.HTTP_400_BAD_REQUEST,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        logger.info(f"Post created by user {self.request.user.username}")