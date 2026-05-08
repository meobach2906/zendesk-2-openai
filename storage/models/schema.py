from typing import Dict, Optional, Any

class Schema:
  def __init__(self, data: Optional[dict] = None):
    data = data or {}

    if not isinstance(data, dict):
      data = data.__dict__

    self.last_article_updated_at: Optional[str] = data.get("last_article_updated_at")


    self.map_synced_article: Dict[str, Any] = data.get("map_synced_article", {})

    self.open_ai: Dict[str, str] = data.get("open_ai", {})