from django.urls import include, path
from .views import PostViewSet, FollowViewSet, GroupViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet, basename="posts")
router.register(r'follow', FollowViewSet, basename="follow")
router.register(r'groups', GroupViewSet, basename="groups")

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]
