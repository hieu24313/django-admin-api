from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        print(request.user)
        return request.user.is_authenticated

    def is_superuser(self, request):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff and request.user.is_active)


class AllowAny(permissions.BasePermission):

    def has_permission(self, request, view):
        return True

    def is_superuser(self, request):
        return True
