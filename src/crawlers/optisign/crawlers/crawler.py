from storage.base_storage.base_storage import BaseStorage
from datetime import datetime, timezone
from src.crawlers.optisign.lib.api_client import ZendeskClient
from src.crawlers.optisign.models.article import ZendeskArticle, Article
from src.utils.utils import utils
from pathlib import Path
from src.services.open_ai.open_ai import OpenAiService
from typing import Optional, Dict, Any
import os

class Crawler:
  def __init__(self, storage: BaseStorage, openai_service: OpenAiService):
    self.storage = storage
    self.openai_service = openai_service
    self.client = ZendeskClient()

    self.next_page: int = 1
    self.per_page: int = 30
    self.is_finished: bool = False

    self.base_dir: Path = Path(__file__).resolve().parents[4]

    os.makedirs(os.path.dirname(self.base_dir / "public"), exist_ok=True)

    self.newest_article_updated_at: Optional[datetime] = None
    self.last_article_updated_at: Optional[datetime] = None

    self.data = self.storage.get()

    if self.data.last_article_updated_at:
      self.last_article_updated_at = datetime.fromisoformat(
        self.data.last_article_updated_at.replace("Z", "+00:00")
      )

    self.state: Dict[str, int] = {
      "total_processed": 0,
      "total_chunk": 0,
      "added": 0,
      "updated": 0,
      "skipped": 0
    }

  def _build_request(self) -> Dict[str, Any]:
    return {
      "endpoint": "/api/v2/help_center/en-us/articles.json",
      "params": {
        "page": self.next_page,
        "per_page": self.per_page,
        "sort_by": "updated_at",
        "sort_order": "desc",
      },
    }

  def start(self) -> None:
    while not self.is_finished:
      self.crawl()

    self.finish()

  def crawl(self) -> None:
    request = self._build_request()
    response = self.client.request(request)

    articles = response.get("articles") or []

    if not articles:
      self.is_finished = True
      return

    for item in articles:
      article: Article = ZendeskArticle.to_article(item)


      if (
        self.newest_article_updated_at is None
        or article.updated_at.timestamp() > self.newest_article_updated_at.timestamp()
      ):
        self.newest_article_updated_at = article.updated_at

      if (
        self.last_article_updated_at
        and article.updated_at.timestamp() < self.last_article_updated_at.timestamp()
      ):
        self.is_finished = True
        return

      synced_article = self.data.map_synced_article.get(str(article.id))

      if synced_article:
        synced_edited_at = datetime.fromisoformat(
          synced_article["edited_at"].replace("Z", "+00:00")
        )

        if synced_edited_at.timestamp() >=  article.edited_at.timestamp():
          print(f"Skipped article id: {article.id}")
          self.state["skipped"] += 1
          continue

        self.state["updated"] += 1
      else:
        self.state["added"] += 1

      file_name = article.build_file_name()
      file_path = self.base_dir / "public" / file_name

      print(f"Start processing article id: {article.id}")
      print(f"Saving markdown file name: {file_name}")

      utils.save_file({
        "file_path": str(file_path),
        "content": article.format_content(),
      })

      print(f"Uploading: {file_name} to OpenAI")

      try:
        results = self.openai_service.process(file_path)
      finally:
        file_path.unlink(missing_ok=True)


      if not synced_article:
        self.data.map_synced_article[article.id] = {
          "article_id": article.id,
          "edited_at": article.edited_at.isoformat(),
        }

      self.data.map_synced_article[article.id]["edited_at"] = article.edited_at.isoformat()

      self.data = self.storage.update(self.data)

      self.state["total_processed"] += 1
      self.state["total_chunk"] += len(results)

    if not self.last_article_updated_at:
      self.is_finished = True
      return

    self.next_page += 1

  def finish(self) -> None:
    if self.newest_article_updated_at:
      self.data.last_article_updated_at = self.newest_article_updated_at.isoformat()
    self.data = self.storage.update(self.data)
    print(
      f"Finished total_processed: {self.state['total_processed']}; "
      f"total_chunk: {self.state['total_chunk']} "
      f"added: {self.state['added']}, updated: {self.state['updated']}, skipped: {self.state['skipped']}"
    )