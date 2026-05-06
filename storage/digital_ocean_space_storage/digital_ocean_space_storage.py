import boto3
import json
from models import schema
from base_storage.base_storage import BaseStorage

from dotenv import load_dotenv
import os

load_dotenv()

class DigitalOceanSpaceStorage(BaseStorage):
  def __init__(self, config):
    config = config or {}

    session = boto3.session.Session()
    self.bucket = config.bucket or  os.getenv("BUCKET")
    self.client = session.client(
      's3',
      region_name='sgp1',
      endpoint_url='https://sgp1.digitaloceanspaces.com',
      aws_access_key_id = config.aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID"),
      aws_secret_access_key = config.aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    response = self.client.get_object(
      Bucket = self.bucket,
      Key = "storage.json"
    )

    content = response["Body"].read()

    self.storage = schema.Schema(json.loads(content))
  
  def save(self):
    self.client.put_object(
      Bucket = self.bucket,
      Key='storage.json',
      Body=json.dumps(self.storage.__dict__)
    )


  

