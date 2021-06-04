from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.urls import path
from rest_framework import routers

from bruhproject.core import views
from django.conf.urls import url
from django.contrib import admin

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'bets', views.BetViewSet)
router.register(r'variants', views.VariantViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'markets', views.MarketViewSet)
router.register(r'wallets', views.WalletViewSet)

urlpatterns = [
    url(r'^bruhproject/', include('bruhproject.core.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='user/login.html.j2'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/bruhproject/'), name='logout'),
    url(r'^register/$', views.register_request, name='register'),
    path('', include(router.urls)),
    path('api/', include('rest_framework.urls', namespace='rest_framework'))
]
