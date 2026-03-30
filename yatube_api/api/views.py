from posts.models import Post, Group, Comment, Follow
from rest_framework import viewsets, permissions, filters
from .serializers import (PostSerializer,
                          CommentSerializer,
                          GroupSerializer,
                          FollowSerializer)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    pagination_class = LimitOffsetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['get', 'put', 'patch', 'delete'],
            url_path=r'comments/(?P<comment_id>\d+)')
    def commentsDetail(self, request, pk=None, comment_id=None):
        post = self.get_object()
        comment = get_object_or_404(Comment, id=comment_id, post=post)

        if request.method == 'GET':
            serializer = CommentSerializer(comment)
            return Response(serializer.data)

        if comment.author != request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')

        if request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = CommentSerializer(
                comment, data=request.data, partial=partial)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

        elif request.method == 'DELETE':
            comment.delete()
            return Response(status=204)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, post=post)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        super(PostViewSet, self).perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        instance.delete()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


User = get_user_model()


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following = serializer.validated_data.get('following')
        if self.request.user == following:
            raise ValidationError('Нельзя подписаться на самого себя')
        if Follow.objects.filter(
            user=self.request.user,
            following=following
        ).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя')
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Метод не разрешен.'},
            status=404
        )
