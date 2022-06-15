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

    def get(self, request, *args, **kwargs):
        """GET method for retrieving specific review."""
        logger.info(f"User {request.user.id} tried to get review with id {self.get_object().id}")

        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """PUT method for updating the whole content of a specific review."""
        logger.info(f"User {request.user.id} tried to change review with id {self.get_object().id}")

        return super().update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """PATCH method for updating specific review fields."""
        logger.info(f"User {request.user.id} tried to change review with id {self.get_object().id}")

        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """DELETE method for removing specific review."""
        logger.info(f"User {request.user.id} tried to delete review with id {self.get_object().id}")

        return super().delete(request, *args, **kwargs)
