class Schema:
  def __init__(self, data):
    data = data or {}
    self.last_article_updated_at: str = data.last_article_updated_at or None

  

  
