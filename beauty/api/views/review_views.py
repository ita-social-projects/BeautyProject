"""This module provides all needed review views."""

import logging

from rest_framework import (status, filters)
from rest_framework.generics import (GenericAPIView, RetrieveUpdateDestroyAPIView)

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import (CustomUser, Review)

from api.serializers.review_serializers import (ReviewAddSerializer, ReviewDisplaySerializer)

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


class ReviewAddView(GenericAPIView):
    """Create Review view.

    This class represents a view which is accessed when someone
    is trying to create a new Review. It makes use of the POST method,
    other methods are not allowed in this view.
    """

    serializer_class = ReviewAddSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, user):
        """This is a POST method of the view."""
        serializer = ReviewAddSerializer(data=request.data)
        author = self.request.user
        to_user = CustomUser.objects.get(pk=user)
        if serializer.is_valid():
            serializer.save(
                from_user=author,
                to_user=to_user,
            )
            logger.info(
                f"User {author} (id = {author.id}) posted a review for"
                f"{to_user} (id = {to_user.id})",
            )
            return Response(status=status.HTTP_201_CREATED)
        else:
            logger.info(
                "Error validating review: "
                f"Field {serializer.errors.popitem()}",
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)
