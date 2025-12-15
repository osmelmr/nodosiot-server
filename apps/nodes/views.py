from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Node
from .serializers import NodeSerializer
from apps.core.permissions import IsAdminOrReadOnly,IsOwnerAndAdminOrReadOnly

# -----------------------------
# CRUD de nodos
# -----------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAdminOrReadOnly])
def node_list_create(request):
    """
    List all nodes or create a new node (admin only for create).
    """
    if request.method == 'GET':
        nodes = Node.objects.filter(is_deleted=False)
        serializer = NodeSerializer(nodes, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = NodeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAdminOrReadOnly])
def node_detail(request, pk):
    """
    Retrieve, update, or delete a node by pk.
    """
    try:
        node = Node.objects.get(pk=pk, is_deleted=False)
    except Node.DoesNotExist:
        return Response({"error": "Node not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = NodeSerializer(node)
        return Response(serializer.data)

    if request.method == 'PATCH':
        if request.user != node.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = NodeSerializer(node, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if request.user != node.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        node.is_deleted = True
        node.save(update_fields=['is_deleted'])
        return Response(status=status.HTTP_204_NO_CONTENT)
