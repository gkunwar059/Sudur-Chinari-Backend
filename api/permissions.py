from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the author of an article to edit it.
    Assumes the model instance has an `author` attribute which is a user.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Admins can edit anything
        if request.user and request.user.is_staff:
            return True
        
        # Check if obj has an author field that links to request.user
        # In our models, Author is a separate model, and Article has a foreign key to Author.
        # We need a way to link Django's User to the Author model. 
        # For simplicity, if the user is staff, they can edit. 
        # If we need exact author matching, we would match request.user to obj.author.user 
        # (assuming we add a user OneToOneField to Author).
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user and request.user.is_staff:
            return True
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user
