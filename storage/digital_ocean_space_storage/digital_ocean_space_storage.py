import boto3
import json
from storage.models import schema
from storage.base_storage.base_storage import BaseStorage
from typing import Any

from dotenv import load_dotenv
import os

load_dotenv()

class DigitalOceanSpaceStorage(BaseStorage):
  def __init__(self, config: Any = None):
    super().__init__()

    config = config or {}

    session = boto3.session.Session()
    self.bucket = config.get("bucket") or os.getenv("BUCKET")
    self.client = session.client(
      's3',
      region_name='sgp1',
      endpoint_url='https://sgp1.digitaloceanspaces.com',
      aws_access_key_id = config.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID"),
      aws_secret_access_key = config.get("aws_secret_access_key") or os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    self._storage = self._load_config()

  def _load_config(self):
    try:
      response = self.client.get_object(
        Bucket = self.bucket,
        Key = "storage.json"
      )

      content = response["Body"].read().decode("utf-8")
      data = json.loads(content)

      return schema.Schema(data)
    except self.client.exceptions.NoSuchKey:
      return schema.Schema()

  def save(self):
    payload = json.dumps(self._storage.__dict__, ensure_ascii=False)

    self.client.put_object(
      Bucket = self.bucket,
      Key='storage.json',
      Body=payload.encode("utf-8"),
      ContentType="application/json"
    )


  

