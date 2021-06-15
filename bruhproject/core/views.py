from itertools import groupby
from operator import attrgetter, imod, itemgetter

from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Wallet, Event, Bet, Market, Variant
from .forms import BetEventForm, NewUserForm
from django.template.loader import render_to_string
import logging
from .minioclass import get_picture_from_minio

# Rest API imports
from django.contrib.auth.models import User
from rest_framework import viewsets, mixins
from rest_framework import permissions
from bruhproject.core.serializers import UserSerializer, BetSerializer, VariantSerializer, WalletSerializer, \
    MarketSerializer, EventSerializer


# REST API Views

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class BetViewSet(viewsets.ModelViewSet):
    serializer_class = BetSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Bet.objects.all()


class VariantViewSet(viewsets.ModelViewSet):
    serializer_class = VariantSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Variant.objects.all()


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Event.objects.all()


class MarketViewSet(viewsets.ModelViewSet):
    serializer_class = MarketSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Market.objects.all()


class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Wallet.objects.all()


# Should we create things like "Services" to move logic to them, instead of processing logic in views?

logger = logging.getLogger(__name__)


def group_required(group):
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name=group)) | u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups, login_url='/bruhproject')


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Wallet(owner=user, name=user.username + "`s wallet", money=0.0, active=True,
                   description="").save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("/bruhproject/")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render(request=request, template_name="user/register.html.j2", context={"register_form": form})


@login_required(login_url='/login')
def index(request):
    user = request.user
    wallets = Wallet.objects.filter(owner=user)
    events = Event.objects.filter(status__gte=0).filter(status__lte=2)[:10]
    user_active_events = get_user_active_events(user)
    events_to_close = Event.objects.filter(status=3)
    pic = get_picture_from_minio("pythonproject","yourpicturesname.jpg")
    return render(request, 'user/home.html.j2',
                  {'username': user.username,
                   'wallets': wallets,
                   'events': events,
                   'active_events': user_active_events,
                   'events_to_close': events_to_close,
                   'pic' : pic })


@login_required(login_url='/login')
def wallet_list(request):
    wallets = Wallet.objects.filter(owner=request.user)
    return render(request, 'wallet/index.html.j2',
                  {'wallets': wallets,
                   'username': request.user.username,
                   })


@login_required(login_url='/login')
def wallet_info(request, wallet_id):
    user = request.user
    wallet = Wallet.objects.get(id=wallet_id)
    # if wallet.owner != user and not user.is_superuser:
    #     messages.error(request, 'You don't own this wallet.!')
    #     return HttpResponseRedirect('/bruhproject/')
    bets = Bet.objects.filter(wallet__id=wallet.id)
    open_bets = bets.filter(chosen_event__status__gte=0).filter(chosen_event__status__lte=2).all()
    closed_bets = bets.filter(chosen_event__status=3).all()
    return render(request, 'wallet/info.html.j2',
                  {'username': user.username,
                   'wallet': wallet,
                   'open_bets': open_bets,
                   'closed_bets': closed_bets})


@login_required(login_url='/login')
def event_list(request):
    events = Event.objects.all()
    return render(request, 'event/index.html.j2',
                  {'events': events,
                   'username': request.user.username,
                   })


@login_required(login_url='/login')
def event_info(request, event_id):
    event = Event.objects.get(id=event_id)
    fields = Event._meta.get_fields()
    variants = Variant.objects.filter(market__event_id=event_id).order_by('market_id')
    results = {0: "Not set", 1: "Not started yet", 2: "Started", 3: "Finished", 4: "Cancelled", 5: "Postponed",
               6: "Interrupted", 7: "Abandoned", 8: "Coverage Lost", 9: "About to start"}
    grouped_variants = [
        {'market_id': k, 'variants': list(vs)}
        for k, vs in groupby(
            variants,
            attrgetter('market_id')
        )
    ]
    bets = Bet.objects.filter(chosen_event__id=event_id)
    template_data = {'event': event,
                     'fields': fields,
                     'grouped_variants': grouped_variants,
                     'bets': bets,
                     'username': request.user.username,
                     'results': results}

    if request.method == 'POST':
        bet_form = BetEventForm(request.POST)
        if bet_form.is_valid():
            bet = bet_form.save(commit=False)
            bet.chosen_event = event
            bet.chosen_event_id = event_id
            bet.wallet.money -= bet.amount
            bet.wallet.save()
            bet.reward = round(bet.amount * bet.chosen_variant.odd, 2)
            bet.save()
            messages.success(request, 'Your bet was accepted.')
            return HttpResponseRedirect(".")
    else:
        bet_form = BetEventForm()
        bet_form.fields['wallet'].queryset = Wallet.objects.filter(owner=request.user)
        variants = Variant.objects.filter(market__event__id=event_id)
        bet_form.fields['chosen_variant'].queryset = variants
    if event.status != 3:
        template_data['bet_form'] = bet_form
    return render(request, 'event/info.html.j2', template_data)


@login_required(login_url='/login')
def ranking_list(request):
    wallets = Wallet.objects.all()
    return render(request, 'ranking/index.html.j2',
                  {'wallets': wallets,
                   'username': request.user.username,
                   })


def get_user_active_bets(user):
    active_bets = Bet.objects.filter(wallet__owner=user, settled=False)
    return active_bets


def get_user_active_events(user):
    active_bets = get_user_active_bets(user)
    active_events = [bet.chosen_event for bet in active_bets]
    return active_events


@login_required(login_url='/login')
def deposit_money_to_wallet(request):
    return render(request, 'wallet/deposit.html.j2',
                  {'username': request.user.username})


@login_required(login_url='/login')
def finish_deposit(request):
    if request.method == 'POST':
        make_deposit = float(request.POST['make_deposit'])
        if make_deposit > 0 and make_deposit != None:
            user = request.user
            wallets = Wallet.objects.filter(owner=user)
            for wallet in wallets:
                wallet.money += make_deposit
                wallet.save()
    return HttpResponseRedirect("/bruhproject")
