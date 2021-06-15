from bruhproject.core.models import Bet, DEFAULT_PROVIDER_ID, Variant
import datetime
import json
import pika
import threading

from django.utils.timezone import now


def fixture_update(update):
    from .models import Bet
    from .models import Event
    from .models import Variant
    from .models import Wallet

    id = update["id"]

    try:
        event = Event.objects.get(id=id)
    except Event.DoesNotExist:
        event = None

    if event:
        event.status = update["status"]
        event.name = update["name"]
        event.start_time = update["start_time"]
    else:
        event = Event(id=int(update["id"]), status=int(update["status"]), start_time=update["start_time"],
                      name=update["name"])

    event.save()


def market_update(update):
    from .models import Market

    try:
        market = Market.objects.get(draft_id=update["id"], event__id=update["fixture_id"])
    except Market.DoesNotExist:
        market = None

    if market:
        update_existing_market(update, market)
    else:
        create_new_market(update)


def update_existing_market(update, market):
    from .models import Variant
    variants = Variant.objects.filter(market__id=market.id)

    for variant in variants:
        for update_variant in update["variants"]:
            if update_variant.id == variant.id:
                variant.name = update_variant.name
                variant.status = update_variant.status
                variant.odd = update_variant.odd
                variant.settlement = update_variant.settlement
            else:
                variant = Variant()
                variant.id = update_variant.id
                variant.name = update_variant.name
                variant.status = update_variant.status
                variant.odd = update_variant.odd
                variant.settlement = update_variant.settlement
                variant.market = market

            if variant.settlement == 1 or variant.settlement == 2:
                print("Settled", variant.id)

            variant.save()

            if update["settle"]:
                for bet in Bet.objects.filter(chosen_variant__id=variant.id):
                    bet.settled = True
                    if variant.settlement == 2:
                        bet.wallet.money += bet.reward
                    elif variant.settlement == 3:
                        bet.reward = bet.amount
                        bet.wallet.money += bet.reward
                    bet.save()
                    bet.wallet.save()


def create_new_market(update):
    from .models import Market
    from .models import Event

    try:
        event = Event.objects.get(id=update["fixture_id"])
    except Event.DoesNotExist:
        event = None

    if event is None:
        return

    market = Market()
    market.name = update["name"]
    market.draft_id = update["id"]
    market.event = event

    market.save()

    for variant in update["variants"]:
        market.variant_set.add(variant, bulk=False)


def prepare_fixture(update):
    updates = []

    for entry in update["Entries"]:
        updates.append({
            "id": entry["FixtureId"],
            "status": int(entry["Fixture"]["Status"]),
            "start_time": datetime.datetime.strptime(entry["Fixture"]["StartDate"], "%Y-%m-%dT%H:%M:%SZ"),
            "name": " - ".join([p["Name"] for p in entry["Fixture"]["Participants"]])})

    return updates


def prepare_markets(update, settle):
    updates = []

    for entry in update["Entries"]:
        for market in entry["Markets"]:
            if not any(filter(lambda p: int(p["Id"]) == DEFAULT_PROVIDER_ID, market["Providers"])):
                continue

            variants = [bet for p in filter(lambda p: p["Id"] == DEFAULT_PROVIDER_ID, market["Providers"]) for bet in
                        p["Bets"]]
            variants = [Variant(id=int(v["Id"]), name=v["Name"], status=int(v["Status"]), odd=float(v["Price"]),
                                settlement=int(v["Settlement"])) for v in variants]

            updates.append({
                "id": int(market["Id"]),
                "fixture_id": int(entry["FixtureId"]),
                "name": market["Name"],
                "variants": variants,
                "settle": settle
            })

    return updates


def rabbit_callback(ch, method, props, body: bytes):
    update = json.loads(body)
    type = int(update["Type"])

    if type == 3:
        for f_update in prepare_fixture(update):
            fixture_update(f_update)
    if type in (2, 5):
        for m_update in prepare_markets(update, type == 5):
            market_update(m_update)


def run_in_background(runnable):
    threading.Thread(target=runnable).start()


def rabbit_background():
    params = pika.ConnectionParameters(
        host="54.217.42.115",
        virtual_host="PreMatch",
        credentials=pika.PlainCredentials("dev", "")
    )

    with pika.BlockingConnection(params) as connection:
        with connection.channel() as channel:
            channel.basic_consume(queue="py_endterm", on_message_callback=rabbit_callback, auto_ack=True)
            channel.start_consuming()
