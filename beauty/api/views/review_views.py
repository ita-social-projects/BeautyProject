"""This module provides all needed review views."""

import logging

from rest_framework import (status, filters)
from rest_framework.generics import (GenericAPIView, RetrieveUpdateDestroyAPIView)

from rest_framework.response import Response

from api.models import Review

from api.serializers.review_serializers import ReviewDisplaySerializer

from api.permissions import IsAdminOrCurrentReviewOwner


logger = logging.getLogger(__name__)


class ReviewDisplayView(GenericAPIView):
    """Generic API for custom GET method."""
    queryset = Review.objects.all()
    serializer_class = ReviewDisplaySerializer
    filter_backends = (filters.OrderingFilter, )
    ordering_fields = ("date_of_publication", )
    ordering = ("-date_of_publication", )

    def get(self, request, to_user):
        """Method for retrieving reviews from the database."""
        queryset = self.queryset.filter(to_user=to_user)
        queryset = super().filter_queryset(queryset)

        if not queryset:
            logger.info(f"Failed to get reviews for user with id {to_user}")
            return Response({"error": "User wasn't reviewed yet"},
                            status=status.HTTP_404_NOT_FOUND)

        queryset = super().paginate_queryset(queryset)
        logger.info(f"Reviews for user with id {to_user} were successfully obtained")
        serialized_data = self.serializer_class(queryset, many=True)
        return Response(serialized_data.data, status=status.HTTP_200_OK)


class ReviewRUDView(RetrieveUpdateDestroyAPIView):
    """View for retrieving specific review."""
    queryset = Review.objects
    serializer_class = ReviewDisplaySerializer
    permission_classes = (IsAdminOrCurrentReviewOwner, )
