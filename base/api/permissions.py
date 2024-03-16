from rest_framework.permissions import BasePermission

class CustomStaffPermission(BasePermission):
    """
    Custom permission to allow access only to users in the 'customstaff_group' group.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.groups.filter(name="CustomStaff").exists()
        return False
