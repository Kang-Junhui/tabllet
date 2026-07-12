"""Token-based authentication endpoints.

Thin views (per CLAUDE.md): validation lives in serializers, token handling in
DRF's authtoken. The SPA stores the returned token and sends it as
``Authorization: Token <key>`` on subsequent requests ("자동 로그인").
"""
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer


def _auth_payload(user):
    """A persistent token + the user, returned by register/login."""
    token, _ = Token.objects.get_or_create(user=user)
    return {"token": token.key, "user": UserSerializer(user).data}


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """POST /api/auth/register/ — {username, password} → {token, user}."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(_auth_payload(user), status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """POST /api/auth/login/ — {username, password} → {token, user}."""
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"detail": "아이디 또는 비밀번호가 올바르지 않습니다."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return Response(_auth_payload(user))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """POST /api/auth/logout/ — invalidate the current user's token."""
    Token.objects.filter(user=request.user).delete()
    return Response({"detail": "로그아웃되었습니다."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """GET /api/auth/me/ — current user (used to validate a stored token)."""
    return Response(UserSerializer(request.user).data)
