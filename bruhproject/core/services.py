from .models import Fixture, Market, Variant, Bet, Wallet


def onFixtureUpdate(update):
    fixture = Fixture.objects.get(fixture_id=update.id)
    if fixture:
        fixture.status = update.status
        fixture.start_date = update.start_date
        fixture.save()
    else:
        new_fixture = Fixture(fixture_id=update.id, participant_1=update.participants[0],
                              participant_2=update.participants[1], start_date=update.start_date, status=update.status)
        new_fixture.save()


def onMarketUpdate(update):
    market = Market.objects.get(market_id=update.id)
    if market:
        variants = Variant.objects.filter(market__market_id=update.id)
        for variant in variants:
            for upd_variant in update.variants:
                if variant.variant_id == upd_variant.variant_id:
                    variant.name = upd_variant.name
                    variant.status = upd_variant.status
                    variant.odd = upd_variant.odd
                    variant.settlement = variant.settlement
                    variant.save()
                    break
            else:
                variant = Variant(name=upd_variant.name, status=upd_variant.status, odd=upd_variant.odd,
                                  settlement=upd_variant.settlement, market_id=upd_variant.market_id,
                                  variant_id=upd_variant.variant_id)
                variant.save()
        market.name = update.name
        market.status = update.status
        market.save()
    else:
        fixture = Fixture.objects.get(fixture_id=update.fixture_id)
        new_market = Market(market_id=update.id, name=update.name, fixture=fixture, status=update.status)
        new_market.save()
        for upd_variant in update.variants:
            variant = Variant(name=upd_variant.name, status=upd_variant.status, odd=upd_variant.odd,
                              settlement=upd_variant.settlement, market_id=upd_variant.market_id,
                              variant_id=upd_variant.variant_id)
            variant.save()


def onVariantSettled(update):
    variant = Variant.objects.get(variant_id=update.id)
    variant.name = update.name
    variant.odd = update.odd
    variant.status = update.status
    variant.settlement = update.settlement
    variant.save()

    if update.settlement == 2:
        betters = Bet.user_set.filter(variant_id=update.id)
        bet = Bet.objects.filter(variant__id=variant.id)
        for better in betters:
            wallet = Wallet.objects.filter(owner__id=better.id)
            wallet.money += bet.amount * variant.odd
            wallet.save()
