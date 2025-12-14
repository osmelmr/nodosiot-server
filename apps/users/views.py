from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer
from apps.core.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# -----------------------------
# CRUD
# -----------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrReadOnly])
def user_list_create(request):
    """
    List all users or create a new user (admin only).
    """
    if request.method == 'GET':
        users = User.objects.filter(is_deleted=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminOrReadOnly])
def user_detail(request, uuid):
    """
    Retrieve, update, or delete a user by UUID.
    """
    try:
        user = User.objects.get(uuid=uuid, is_deleted=False)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        user.is_deleted = True
        user.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------
# LOGIN
# -----------------------------

@api_view(['POST'])
@permission_classes([AllowAny])  # acceso público para login
def user_login(request):
    """
    Login usando email y password.
    Devuelve access y refresh tokens junto con datos del usuario.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"error": "Email and password required"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    return Response({
        "user": {
            "uuid": str(user.uuid),
            "email": user.email,
            "role": user.role,
        },
        "access": str(access),
        "refresh": str(refresh),
    }, status=status.HTTP_200_OK)
