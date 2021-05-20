from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Wallet, Fixture, Market, Variant, Bet
from .forms import BetEventForm, NewEventForm, CloseEventForm, NewUserForm
from django.template.loader import render_to_string
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)


# Should we create things like "Services" to move logic to them, instead of processing logic in views?

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
                   description="", ).save()
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
    events = Fixture.objects.filter(start_date=timezone.now(), open=True)
    user_active_events = get_user_active_events(user)
    return render(request, 'user/home.html.j2',
                  {'username': user.username,
                   'wallets': wallets,
                   'events': events,
                   'active_events': user_active_events})


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
    bets = Bet.objects.filter(user__username=user.username)
    variants = Bet.variant_set.filter(id=bets.id)
    open_bets = variants.filter(settlement=0).all()
    closed_bets = variants.filter(~Q(settlement=0)).all()
    return render(request, 'wallet/info.html.j2',
                  {'username': user.username,
                   'wallet': wallet,
                   'open_bets': open_bets,
                   'closed_bets': closed_bets})


@login_required(login_url='/login')
def event_list(request):
    events = Bet.objects.all()
    return render(request, 'event/index.html.j2',
                  {'events': events,
                   'username': request.user.username,
                   })


@login_required(login_url='/login')
def event_info(request, event_id):
    event = Fixture.objects.get(id=event_id)
    if event.end_time < timezone.now() and event.open:
        event.to_close = True
    else:
        event.to_close = False
    fields = Bet._meta.get_fields()
    bets = Bet.objects.filter(fixture__id=event_id)
    template_data = {'event': event,
                     'fields': fields,
                     'bets': bets,
                     'username': request.user.username, }
    if request.method == 'POST':
        bet_form = BetEventForm(request.POST)
        if bet_form.is_valid():
            bet = bet_form.save(commit=False)
            bet.event = event
            if bet.chosen_result == 0:
                bet.odd = event.draw_odd
            elif bet.chosen_result == 1:
                bet.odd = event.home_odd
            elif bet.chosen_result == 2:
                bet.odd = event.away_odd
            bet.wallet.money -= bet.value
            bet.wallet.save()
            bet.reward = round(bet.value * bet.odd, 2)
            bet.save()
            messages.success(request, 'Your bet was accepted.')
            return HttpResponseRedirect(".")
    else:
        bet_form = BetEventForm()
        bet_form.fields['wallet'].queryset = Wallet.objects.filter(owner=request.user)
    if event.open and event.start_time > timezone.now():
        template_data['bet_form'] = bet_form
        # if not request.user.is_superuser:
        #     bets = bets.filter(wallet__owner=request.user)
        #     template_data['bets'] = bets
    return render(request, 'event/info.html.j2', template_data)


@login_required(login_url='/login')
def ranking_list(request):
    wallets = Wallet.objects.all()
    return render(request, 'ranking/index.html.j2',
                  {'wallets': wallets,
                   'username': request.user.username,
                   })


def get_user_active_bets(user):
    active_bets = Bet.objects.filter(wallet__owner=user, event__start_time__lte=timezone.now(),
                                     event__end_time__gte=timezone.now())
    return active_bets


def get_user_active_events(user):
    active_bets = get_user_active_bets(user)
    active_events = [bet.event for bet in active_bets]
    return active_events


@login_required(login_url='/login')
def deposit_money_to_wallet(request):
    return render(request, 'wallet/deposit.html.j2',
                  {'username': request.user.username})


@login_required(login_url='/login')
def finish_deposit(request):
    if request.method == 'POST':
        make_deposit = float(request.POST['make_deposit'])
        if make_deposit > 0 and make_deposit is not None:
            user = request.user
            wallets = Wallet.objects.filter(owner=user)
            for wallet in wallets:
                wallet.money += make_deposit
                wallet.save()
    return HttpResponseRedirect("/bruhproject")
