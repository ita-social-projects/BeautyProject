from django.db.models import Q
from rest_framework.generics import ListCreateAPIView, get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import CustomUser, Order
from .serializers.serializers_customuser import CustomUserDetailSerializer, \
    UserOrderDetailSerializer
from .serializers.serializers_customuser import CustomUserSerializer


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for users custom POST methods"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for users custom GET, PUT and DELETE methods.
    RUD - Retrieve, Update, Destroy"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    def perform_destroy(self, instance):
        """Reimplementation of the DESTROY (DELETE) method.
        Makes current user inactive by changing its' field
        """
        if instance.is_active:
            instance.is_active = False
            instance.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CustomUserOrderDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for orders custom GET, PUT and DELETE methods.
       RUD - Retrieve, Update, Destroy"""

    queryset = Order.objects.all()
    serializer_class = UserOrderDetailSerializer
    multiple_lookup_fields = ('user', 'id')

    def get_object(self):
        """Method for getting order objects by using both order user id
         and order id lookup fields."""
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, Q(customer=self.kwargs['user']) |
                                Q(specialist=self.kwargs['user']),
                                id=self.kwargs['id'])
        self.check_object_permissions(self.request, obj)
        return obj
