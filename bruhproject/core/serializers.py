from django.contrib.auth.models import User, Group
from rest_framework import serializers

from bruhproject.core.models import Bet, Variant, Event, Market, Wallet


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class BetSerializer(serializers.HyperlinkedModelSerializer):
    wallet = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='wallet-detail')
    chosen_variant = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='variant-detail')
    chosen_event = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='event-detail')

    url = serializers.HyperlinkedIdentityField(view_name='bet-detail')

    class Meta:
        model = Bet
        fields = '__all__'


class VariantSerializer(serializers.HyperlinkedModelSerializer):
    market = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='market-detail')
    url = serializers.HyperlinkedIdentityField(view_name='variant-detail')

    class Meta:
        model = Variant
        fields = '__all__'


class EventSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='event-detail')

    class Meta:
        model = Event
        fields = '__all__'


class MarketSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='market-detail')
    event = serializers.HyperlinkedRelatedField(many=False, read_only=True, view_name='event-detail')

    class Meta:
        model = Market
        fields = '__all__'


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='wallet-detail')
    owner = serializers.HyperlinkedIdentityField(view_name='user-detail')

    class Meta:
        model = Wallet
        fields = '__all__'
