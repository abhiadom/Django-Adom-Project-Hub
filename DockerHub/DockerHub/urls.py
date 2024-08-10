from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('login/', include('django.contrib.auth.urls')),
    path('login/', include('members.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configure Admin Titles
admin.site.site_header = "Docker Hub Administration Page"
admin.site.site_title = "Browser Title"
admin.site.index_title = "Welcome To The Admin Area..."