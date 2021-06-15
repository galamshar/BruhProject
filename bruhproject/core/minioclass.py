from base64 import decode
from minio import Minio
import minio
from urllib3.response import HTTPResponse
from PIL import Image
from io import BytesIO
import base64

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

def get_picture_from_minio(bucket, picture_name):
    return base64.b64encode(client.get_object(bucket, picture_name).read()).decode("ascii")
