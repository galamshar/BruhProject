import base64

from minio import Minio

from .models import Market, Variant, Bet, Wallet


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
