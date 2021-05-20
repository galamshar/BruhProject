from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

BET_SIDE = (
    (0, 'X'),
    (1, '1'),
    (2, '2')
)


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


class Fixture(models.Model):
    fixture_id = models.IntegerField(blank=False, verbose_name="Fixture Id")
    participant_1 = models.CharField(max_length=50, blank=False,
                                     verbose_name='First team\'s name')
    participant_2 = models.CharField(max_length=50, blank=False,
                                     verbose_name='Second team\'s name')
    status = models.IntegerField(blank=False, verbose_name="Status of fixture")
    start_date = models.DateTimeField(default=datetime.now, verbose_name='Start date')


class Market(models.Model):
    market_id = models.IntegerField(blank=False, verbose_name="Market Id")
    name = models.CharField(max_length=100, blank=False,
                            verbose_name='Market name')
    fixture = models.ForeignKey(Fixture, null=False, verbose_name='Fixture')
    status = models.IntegerField(blank=False, verbose_name="Status of fixture")


class Variant(models.Model):
    variant_id = models.IntegerField(blank=False, verbose_name="Variant Id")
    market = models.ForeignKey(Market, null=False, verbose_name="Market Id")
    name = models.CharField(max_length=100, blank=False,
                            verbose_name='Variant name')
    odd = models.FloatField(default=1.0, blank=False,
                            verbose_name='Odd',
                            validators=[MinValueValidator(1.0, 'The minimum Odd is 1.0.')])
    status = models.IntegerField(blank=False, verbose_name="Status of variant")
    settlement = models.IntegerField(blank=False, verbose_name="Settlement")


class Bet(models.Model):
    user = models.ForeignKey(User, null=False, verbose_name="Bet owner")
    fixture = models.ForeignKey(Fixture, null=False, verbose_name="Fixture of bet")
    market = models.ForeignKey(Market, null=False, verbose_name="Market of bet")
    variant = models.ForeignKey(Variant, null=False, verbose_name="Variant of bet")
    amount = models.FloatField(blank=False,
                               verbose_name='Bet\'s size',
                               validators=[MinValueValidator(0.0, 'The value of the bet must not be negative!')])


class Friendship(models.Model):
    person = models.ForeignKey(User, null=False,
                               verbose_name='Person', related_name='person', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, null=False,
                               verbose_name='Friend', related_name='friend', on_delete=models.CASCADE)
    acceptance = models.BooleanField(null=False, verbose_name='Acceptance of familiarity')
