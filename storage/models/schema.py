class Schema:
  def __init__(self, data):
    data = data or {}
    self.last_article_updated_at: str = data.last_article_updated_at or None
    self.map_synced_article: dict[str, _Article]  = data.map_synced_article or {}
class _Article:
  def __init__(self, article_id, edited_at):
    self.article_id = article_id
    self.edited_at = edited_at