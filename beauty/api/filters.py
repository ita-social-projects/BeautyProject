"""Module with filter classes."""

from django_filters import rest_framework as filters

from .models import Service


class ServiceFilter(filters.FilterSet):
    """Filter services by options represented in Meta class fields."""

    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_duration = filters.NumberFilter(field_name="duration", lookup_expr="gte")
    max_duration = filters.NumberFilter(field_name="duration", lookup_expr="lte")

    class Meta:
        """Meta class for ServiceFilter."""
        model = Service
        fields = ["name", "price", "min_price", "max_price", "duration", "min_duration",
                  "max_duration"]
