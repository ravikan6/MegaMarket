"""
URL configuration for MegaMarket project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from Api.urls import version_1
from Api.views import image_upload, main
from MegaMarket import settings
from oauth2_provider import urls as oauth2_urls
from Admin.urls import webhook, auth

urlpatterns = [
    path('', main),
    path('admin/', admin.site.urls),
    path('api/v1/', include(version_1)),
    path('upload_image/', image_upload, name='image_upload'),
    path("o/", include(oauth2_urls)),
    path('webhook/', include(webhook)),
    path('auth/', include(auth)),
] 

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)