from django.db.models import Q
from rest_framework.generics import ListCreateAPIView, get_object_or_404
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from .models import CustomUser, Order
from .serializers.serializers_customuser import CustomUserDetailSerializer, \
    UserOrderDetailSerializer
from .serializers.serializers_customuser import CustomUserSerializer


class CustomUserListCreateView(ListCreateAPIView):
    """Generic API for custom POST method"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    # Permissions
    # line with max chars in code


class CustomUserDetailRUDView(RetrieveUpdateDestroyAPIView):
    """Generic API for custom GET, PUT and DELETE method.
    RUD - Retrieve, Update, Destroy"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserDetailSerializer

    # Permissions
    # rest git hub


class CustomUserOrderDetailGenerics(RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = UserOrderDetailSerializer
    multiple_lookup_fields = ('user', 'id')

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, Q(customer=self.kwargs['user']) |
                                Q(specialist=self.kwargs['user']),
                                id=self.kwargs['id'])
        self.check_object_permissions(self.request, obj)
        return obj