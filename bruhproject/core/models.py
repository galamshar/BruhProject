from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

DEFAULT_PROVIDER_ID = 8

class Wallet(models.Model):
    owner = models.ForeignKey(User, null=False,
                              verbose_name='Wallet owner', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False,
                            verbose_name='Wallet name')
    description = models.TextField(blank=True,
                                   verbose_name='Wallet description')
    money = models.FloatField(blank=False,
                              verbose_name='Balance')
    active = models.BooleanField(default=True, blank=False,
                                 verbose_name='Wallet is active')
    creation_time = models.DateTimeField(default=datetime.now,
                                         verbose_name='Creation time')

    def __str__(self):
        return self.name

    def get_lifetime(self):
        return (timezone.now() - self.creation_time).days


class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.IntegerField()
    name = models.CharField(max_length=150)
    start_time = models.DateTimeField(blank=False, verbose_name='Event start time')

class Market(models.Model):
    name = models.CharField(max_length=150)
    event = models.ForeignKey(Event, null=False, on_delete=models.CASCADE)
    draft_id = models.IntegerField()

class Variant(models.Model):
    id = models.BigIntegerField(primary_key=True)
    market = models.ForeignKey(Market, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    status = models.IntegerField()
    odd = models.FloatField()
    settlement = models.IntegerField()

class Bet(models.Model):
    wallet = models.ForeignKey(Wallet, null=False, on_delete=models.CASCADE)
    chosen_variant = models.ForeignKey(Variant, null=False, on_delete=models.CASCADE)
    chosen_event = models.ForeignKey(Event, null=False, on_delete=models.CASCADE)
    settled = models.BooleanField()
    amount = models.FloatField()
    reward = models.FloatField()

    def __str__(self):
        return 'Bet: ' + self.event.name


class Friendship(models.Model):
    person = models.ForeignKey(User, null=False,
                               verbose_name='Person', related_name='person', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, null=False,
                               verbose_name='Friend', related_name='friend', on_delete=models.CASCADE)
    acceptance = models.BooleanField(null=False, verbose_name='Acceptance of familiarity')
