"""This module provides all location`s views."""

import logging

from api.models import Location
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from api.serializers.business_serializers import LocationSerializer


logger = logging.getLogger(__name__)


class LocationCreateView(CreateAPIView):
    """View for location creation."""

    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LocationRUDView(RetrieveUpdateDestroyAPIView):
    """RUD View for retrieve & editing the business location.

    RUD - Retrieve, Update, Destroy.
    """

    queryset = Location.objects.all()
    serializer_class = LocationSerializer
