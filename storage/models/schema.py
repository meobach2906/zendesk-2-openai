from typing import Dict, Optional

class _Article:
  def __init__(self, article_id: str, edited_at: str):
    self.article_id = article_id
    self.edited_at = edited_at

  def to_dict(self) -> dict:
    return {
      "article_id": self.article_id,
      "edited_at": self.edited_at
    }

  @classmethod
  def from_dict(cls, data: dict):
    return cls(
      article_id=data.get("article_id"),
      edited_at=data.get("edited_at")
    )


class Schema:
  def __init__(self, data: Optional[dict] = None):
    data = data or {}

    self.last_article_updated_at: Optional[str] = data.get("last_article_updated_at")

    raw_map = data.get("map_synced_article", {})

    self.map_synced_article: Dict[str, _Article] = {
      k: _Article.from_dict(v) if isinstance(v, dict) else v
      for k, v in raw_map.items()
    }

    self.open_ai: Dict[str, str] = data.get("open_ai", {})