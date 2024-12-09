from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from app import views
from allauth.account.views import PasswordChangeView
from django.views.generic import TemplateView


urlpatterns = [
    path('accounts/first_page_login/', views.first_page_login, name='first_page_login'), # страница с выбором входа (через соц сеть или по почте)
    path('accounts/login/', views.CustomLoginView.as_view(), name='account_login'),
    path('accounts/password/reset/', views.CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/password/change/done/', TemplateView.as_view(template_name='account/password_change_done.html'), name='account_password_change_done'),
    path('accounts/password/change/', PasswordChangeView.as_view(success_url='done/'), name='password_change'),
    path('accounts/password_reset/notification/', views.password_reset_notification, name='password_reset_notification'), # сменить пароль, если зареган через соц сеть
    path('accounts/', include('allauth.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),
    path('', include('app.urls', namespace='app')),
]

urlpatterns += staticfiles_urlpatterns()
