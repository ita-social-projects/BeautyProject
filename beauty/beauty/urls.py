"""beauty URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
1. Add an import:  from my_app import views
2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
1. Add an import:  from other_app.views import Home
2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
1. Import the include() function: from django.urls import include, path
2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.views import UserActivationView, ResetPasswordView


@api_view(['GET'])
def api_root(request, format=None):
    return Response(
        {'users': reverse('api:user-list', request=request, format=format)}
    )


urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path(
        'activate/<uidb64>/<token>/',
        UserActivationView.as_view(),
        name='user-activation'
    ),
    path(
        'password/reset/confirm/<uidb64>/<token>/',
        ResetPasswordView.as_view(),
        name='reset-password'
    ),
    # path('api/v1/auth/', include('djoser.urls')),
    # path('api/v1/auth_token/', include('djoser.urls.authtoken')),
    path('api/v1/', include('api.urls', namespace="api")),
    #path(
    #    'api-auth/',
    # include('rest_framework.urls', namespace='rest_framework')
    # ),
    path(r'auth/', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.jwt'))

]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )