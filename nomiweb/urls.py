from django.contrib import admin
from django.urls import path ,include
from apps.login.views import custom_400 ,custom_403,custom_404 ,custom_500
from django.conf import settings
from django.conf import settings
from django.conf.urls.static import static

# Importa Django Debug Toolbar solo si DEBUG está activado
if settings.DEBUG:
    import debug_toolbar

urlpatterns = [
    path('', include(('apps.login.urls', 'login'))),
    path('accounts/', include('allauth.urls')),
    path('', include('allauth.socialaccount.urls')),
    path('employees/', include(('apps.employees.urls', 'employees'))),
    path('companies/', include(('apps.companies.urls', 'companies'))),
    path('admin/', include(('apps.administrator.urls', 'admin'))),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Si DEBUG está activado, agrega las URLs de Django Debug Toolbar
if settings.DEBUG:
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

#handler400 = custom_400  # Configura la vista custom_400 para manejar el error 400
#handler403 = custom_403  # Configura la vista custom_403 para manejar el error 403
handler404 = 'apps.login.views.custom_404' # Configura la vista custom_404 para manejar el error 404
handler500 = 'apps.login.views.custom_500'  # Configura la vista custom_500 para manejar el error 500

