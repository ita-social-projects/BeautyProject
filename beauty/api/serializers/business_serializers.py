from rest_framework import serializers
from api.models import Business


class BusinessListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = ('name', 'type', 'owner', 'address')

