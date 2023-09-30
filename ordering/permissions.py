from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access it.
    """

    def has_permission(self, request, view):
        
        if hasattr(view, 'action'):
            authenticated_actions = ['list', 'retrieve', 'add_to_cart']
            if view.action in authenticated_actions:
                return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj): 
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        return False

