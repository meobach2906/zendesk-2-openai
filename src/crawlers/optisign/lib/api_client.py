import os
import requests

from dotenv import load_dotenv
from typing import Optional, Dict, Any, Tuple

from utils.utils import utils

load_dotenv()


class ZendeskClient:
  def __init__(self, config: Optional[Any] = None):
    config = config or {}

    self.base_url: str = config.get("zendesk_base_url") or os.getenv("ZENDESK_BASE_URL", "")
    self.timeout: int = int(
      config.get("zendesk_timeout")
      or os.getenv("ZENDESK_TIMEOUT")
      or 10
    )

    self.auth: Optional[Tuple[str, str]] = None

    email = config.get("zendesk_email") or os.getenv("ZENDESK_EMAIL")
    token = config.get("zendesk_token") or os.getenv("ZENDESK_TOKEN")

    if email and token:
      self.auth = (f"{email}/token", token)

  def request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    if not request_data:
      raise ValueError("request is required")

    endpoint = request_data.get("endpoint")
    if not endpoint:
      raise ValueError("endpoint is required")

    method = request_data.get("method", "get").lower()
    params = request_data.get("params")
    body = request_data.get("body")

    url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _do_request():
      response = requests.request(
        method=method,
        url=url,
        params=params,
        json=body,
        auth=self.auth,
        timeout=self.timeout,
      )
      response.raise_for_status()
      return response

    response = utils.retry(_do_request)

    return response.json()