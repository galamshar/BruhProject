import base64

from minio import Minio

from .models import Market, Variant, Bet, Wallet


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


client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False)


def get_banners(bucket):
    objects = client.list_objects("bruhproject")
    images = []
    for obj in objects:
        images.append(base64.b64encode(client.get_object("bruhproject",obj.object_name).read()).decode('ascii'))
    return images
