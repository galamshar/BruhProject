from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^bruhproject/', include('bruhproject.core.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='user/login.html.j2'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page = '/bruhproject/'), name='logout'),

]
