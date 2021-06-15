from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^wallet/$', views.wallet_list, name='wallet list'),
    url(r'^wallet/(?P<wallet_id>[0-9]+)/$', views.wallet_info, name='wallet info'),
    url(r'^event/$', views.event_list, name='event list'),
    url(r'^event/(?P<event_id>[0-9]+)/$', views.event_info, name='event info'),
    url(r'^ranking/$', views.ranking_list, name='ranking list'),
    url(r'^deposit/$', views.deposit_money_to_wallet, name='deposit'),
    url(r'^deposit/new/$', views.finish_deposit, name='deposit finish'),
    url(r'^bet/sell/(?P<bet_id>[0-9]+)/$', views.sell_bet, name='sell bet')
]