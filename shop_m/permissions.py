from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  
        return request.user.is_staff  

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_permission(self, request, view):
       
        if hasattr(view, 'action') and view.action == 'list':
            return False  
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

