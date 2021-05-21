from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Wallet, Event, Bet
from .forms import BetEventForm, NewUserForm
from django.template.loader import render_to_string
import logging
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
    events = Event.objects.filter(start_time__gte=timezone.now(), open=True)
    user_active_events = get_user_active_events(user)
    events_to_close = Event.objects.filter(end_time__lte=timezone.now(), open=True)
    return render(request, 'user/home.html.j2',
                  {'username': user.username,
                   'wallets': wallets,
                   'events': events,
                   'active_events': user_active_events,
                   'events_to_close': events_to_close})


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
    bets = Bet.objects.filter(wallet=wallet)
    open_bets = bets.filter(open=True).all()
    closed_bets = bets.filter(open=False).all()
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
    return render(request, 'event/info.html.j2')
    
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
        if(make_deposit > 0 and make_deposit != None):
            user = request.user
            wallets = Wallet.objects.filter(owner=user)
            for wallet in wallets:
                wallet.money += (make_deposit)
                wallet.save()
    return HttpResponseRedirect("/bruhproject")