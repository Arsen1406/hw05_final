from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls', namespace='posts')),
    path('about/', include('about.urls', namespace='about')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
]
handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'
handler500 = 'core.views.technical_500_response'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
