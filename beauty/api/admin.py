from django.contrib import admin
from .models import CustomUser
# Register your models here.


class CustomerUserAdminSerializer(admin.ModelAdmin):
    """User serializer"""
    class Meta:
        """Just an additional class"""
        model = CustomUser
        fields = "__all__"


admin.site.register(CustomUser, CustomerUserAdminSerializer)
