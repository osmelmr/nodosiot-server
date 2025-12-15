# apps/core/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and request.user.role == 'admin'
        return request.user.is_authenticated

class IsOwnerAndAdminOrReadOnly(permissions.BasePermission):
    """
    - Lectura (GET): cualquier usuario autenticado
    - Escritura (PATCH, DELETE):
        SOLO si el usuario es ADMIN y además es OWNER del objeto
    """

    def has_permission(self, request, view):
        # Para cualquier acción, debe estar autenticado
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Lectura: permitido a cualquier usuario autenticado
        if request.method in permissions.SAFE_METHODS:
            return True

        # Escritura: DEBE ser admin Y dueño del objeto
        return (
            request.user.role == 'admin'
            and obj.user == request.user
        )