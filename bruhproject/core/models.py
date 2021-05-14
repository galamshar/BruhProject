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
    template = models.BooleanField(default=False, blank=False,
                                   verbose_name='Wallet template')

    def __str__(self):
        return self.name

    def get_lifetime(self):
        return (timezone.now() - self.creation_time).days


class Event(models.Model):
    author = models.ForeignKey(User, null=False,
                               verbose_name='Author of the event', on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=False,
                                      verbose_name='Event start time')
    end_time = models.DateTimeField(blank=False,
                                    verbose_name='Event end time')
    creation_time = models.DateTimeField(default=datetime.now, blank=False,
                                         verbose_name='Event creation time')
    name = models.CharField(max_length=100, blank=False,
                            verbose_name='Event name')
    description = models.TextField(blank=True,
                                   verbose_name='Description of the event')
    home_name = models.CharField(max_length=50, blank=False,
                                 verbose_name='First team\'s name')
    away_name = models.CharField(max_length=50, blank=False,
                                 verbose_name='Second team\'s name')
    home_odd = models.FloatField(default=1.0, blank=False,
                                 verbose_name='Odd for the first team',
                                 validators=[MinValueValidator(1.0, 'The minimum Odd is 1.0.')])
    draw_odd = models.FloatField(default=1.0, blank=False,
                                 verbose_name='Odds for a draw',
                                 validators=[MinValueValidator(1.0, 'The minimum Odd is 1.0.')])
    away_odd = models.FloatField(default=1.0, blank=False,
                                 verbose_name='Odds for the second team',
                                 validators=[MinValueValidator(1.0, 'The minimum Odd is 1.0.')])
    open = models.BooleanField(default=True, blank=False,
                               verbose_name='Event not included')
    result = models.IntegerField(null=True, blank=True,
                                 verbose_name='Event result',
                                 choices=BET_SIDE)

    def is_active(self):
        return self.start_time <= timezone.now() and self.end_time > timezone.now()

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('can_close', "Can insert result and close event."),
        )


class Bet(models.Model):
    wallet = models.ForeignKey(Wallet, null=False,
                               verbose_name='Wallet', on_delete=models.CASCADE)
    chosen_result = models.IntegerField(blank=False, choices=BET_SIDE,
                                        verbose_name='Result')
    event = models.ForeignKey(Event, null=False,
                              verbose_name='Event', on_delete=models.CASCADE)
    value = models.FloatField(blank=False,
                              verbose_name='Bet\'s size',
                              validators=[MinValueValidator(0.0, 'The value of the bet must not be negative!')])
    odd = models.FloatField(blank=False,
                            verbose_name='Betting odds')
    reward = models.FloatField(blank=False,
                               verbose_name='Possible win')
    creation_time = models.DateTimeField(default=datetime.now, blank=False,
                                         verbose_name='Creation time')
    open = models.BooleanField(default=True, blank=False,
                               verbose_name='Unsettled bet')
    won = models.NullBooleanField(null=True, blank=True,
                                  verbose_name='Unsettled bet')

    def __str__(self):
        return 'Bet: ' + self.event.name


class Friendship(models.Model):
    person = models.ForeignKey(User, null=False,
                               verbose_name='Person', related_name='person', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, null=False,
                               verbose_name='Friend', related_name='friend', on_delete=models.CASCADE)
    acceptance = models.BooleanField(null=False, verbose_name='Acceptance of familiarity')
