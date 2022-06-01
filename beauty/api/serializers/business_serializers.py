from rest_framework import serializers
from api.models import Business, CustomUser


class BusinessListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('name', 'type', 'owner', 'description')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        owner = CustomUser.objects.filter(id=data["owner"]).first()
        data["owner"] = owner.get_full_name()
        return data
