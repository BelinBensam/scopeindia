"""
URL configuration for scope_project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Built-in Django Admin (secondary / technical maintenance)
    path('django-admin/', admin.site.urls),

    # 1. Custom Admin Panel (Primary Staff Portal)
    path('admin-panel/', include('admin_panel.urls')),

    # 2. Student Dashboard
    path('dashboard/', include('dashboard.urls')),

    # 3. Public Website (Default root routing)
    path('', include('main.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
