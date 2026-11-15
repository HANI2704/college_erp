"""College ERP URL Configuration"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('account.urls')),
    path('student/', include('student.urls')),
    path('faculty/', include('faculty.urls')),
    path('admin-panel/', include('ERP.urls')),
    path('lms/', include('LMS.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
