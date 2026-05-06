from storage.base_storage.base_storage import BaseStorage
from datetime import datetime
from lib.api_client import ZendeskClient
from models.article import ZendeskArticle, Article
from utils.utils import Utils
from pathlib import Path
from services.open_ai.open_ai import OpenAiService

class Crawler:
  def __init__(self, storage: BaseStorage, openai_service: OpenAiService):
    self.storage = storage
    self.openai_service = openai_service
    self.client = ZendeskClient()
    self.next_page = 1
    self.per_page = 30
    self.is_finished = False
    self.newest_article_update_at = None
    self.utils = Utils()
    self.base_dir = Path(__file__).resolve().parent

  def _build_request(self, data):
    request = {
      "endpoint": "/api/v2/help_center/en-us/articles.json",
      "params": {
        "page": self.next_page,
        "per_page": self.per_page,
        "sort_by": "updated_at",
        "sort_order": "desc",
      }
    }

    if data.last_article_updated_at:
      request.params['start_time'] = int(datetime.fromisoformat(data.last_article_updated_at.replace("Z", "+00:00")))

    return request    
  
  def start(self):
    while not self.is_finished:
      self.crawl()

    if self.newest_article_update_at:
      data = self.storage.get()
      data.last_article_updated_at = self.newest_article_update_at
      self.storage.update(data)

    return

  
  def crawl(self):

    data = self.storage.get()

    request = self._build_request()

    response = self.client.request(request)

    self.last_article_updated_at = None

    if data.last_article_updated_at:
      self.last_article_updated_at = datetime.fromisoformat(data.last_article_updated_at.replace("Z", "+00:00"))

    articles = response.get('articles') or []

    if len(articles) == 0:
      self.is_finished = True
      return

    for item in articles or []:
      article: Article = ZendeskArticle(item).to_article()
      updated_at = datetime.fromisoformat(article.updated_at.replace("Z", "+00:00"))
      if self.last_article_updated_at and self.last_article_updated_at < updated_at:
        self.is_finished = True
        return
      if not self.newest_article_update_at:
        self.newest_article_update_at = article.updated_at

      file_path = self.base_dir + '/public/' + article.build_file_name()
      self.utils.save_file({
        "file_path": file_path,
        "content": article.format_content(),
      })

      self.openai_service.process(file_path)

    if not self.last_article_updated_at:
      self.is_finished = True
      return

    self.next_page += 1

    return
  
  def finish(self):
    data = self.storage.get()
    data.last_article_updated_at = self.last_article_updated_at
    self.storage.update(data)

