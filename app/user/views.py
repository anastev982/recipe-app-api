"""Views for the user API."""

from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, authentication, permissions, status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from user.serializers import UserSerializer, AuthTokenSerializer
from user.serializers import APIRootSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

import logging

logger = logging.getLogger(__name__)


User = get_user_model()


class CustomObtainAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]  # Allow any user to obtain a token

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request=request, username=email, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=400)

        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class TokenViewSet(viewsets.ViewSet):
    """ViewSet for managing user tokens."""

    serializer_class = AuthTokenSerializer

    def create(self, request):
        """Authenticate and create a token for the user."""
        from user.views import CustomObtainAuthToken

        logger.debug(f"Create user response from: {request.data}")
        return CustomObtainAuthToken.as_view()(request._request)

    @action(detail=False, methods=["delete"])
    def delete(self, request):
        """Delete the user's token to log them uot."""
        if request.user.is_authenticated:
            request.user.auth_token.delete()
            logger.debug(f"Token deleted for user: {request.user.email}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Not authenticated"}, status=status.HTTP_403_FORBIDDEN
        )


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for handling user opeeations.)"""

    User = get_user_model()
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create"]:
            return [AllowAny()]
        return super().get_permissions()

    def me(self, request):
        """Retrieve the authenticated user."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Cretaer a new user."""
        serializer.save()


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage user in the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class APIRootView(generics.GenericAPIView):
    """API root view.."""

    serializer_class = APIRootSerializer

    def get(self, request):
        """Return the API root endpoints."""
        response_data = {
            "schema": request.build_absolute_uri("/api/schema/"),
            "docs": request.build_absolute_uri("/api/docs/"),
            "user": request.build_absolute_uri("/api/user/"),
        }
        serializer = self.get_serializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
