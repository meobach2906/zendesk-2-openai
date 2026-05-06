import requests

from dotenv import load_dotenv
import os

from utils.utils import utils

load_dotenv()

class ZendeskClient:
  def __init__(self, config):
    config = config or {}

    self.base_url = config.zendesk_base_url or os.getenv("ZENDESK_BASE_URL")
    self.auth = None
    self.timeout = config.zendesk_timeout or os.getenv("ZENDESK_TIMEOUT") or 10000

    email = config.zendesk_email or os.getenv("ZENDESK_EMAIL")
    token = config.zendesk_token or os.getenv("ZENDESK_TOKEN")

    if email and token:
      self.auth = (f"{email}/token", token)

  def request(self, request = None):
    if not request:
      raise ValueError("request is required")
    endpoint = request.get('endpoint')
    if not endpoint:
      raise ValueError("endpoint is required")

    method = request.get('method', 'get').lower()
    params = request.get('params')
    body = request.get('body')

    def request():
      response = requests.request(method, f"{self.base_url}/{endpoint}", params=params, json=body, auth=self.auth, timeout=self.timeout)
      response.raise_for_status()
      return response

    response = utils.retry(request)

    return response.json()