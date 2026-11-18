from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('utilisateurs/', include('utilisateurs.urls')),
    path('catalogue/', include('catalogue.urls')),
    path('partenaires/', include('partenaires.urls')),
    path('achats-stock/', include('achats_stock.urls')),
    path('ventes/', include('ventes.urls')),
    path('rapports/', include('rapports.urls')),

    # Gestion du mot de passe
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='utilisateurs/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='utilisateurs/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='utilisateurs/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='utilisateurs/password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)