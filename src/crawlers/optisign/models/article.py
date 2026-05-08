from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from markdownify import markdownify as md


class Article:
  def __init__(
    self,
    id: int,
    url: str,
    html_url: str,
    author_id: int,
    comments_disabled: bool,
    draft: bool,
    promoted: bool,
    position: int,
    vote_sum: int,
    vote_count: int,
    section_id: int,
    created_at: datetime,
    updated_at: datetime,
    name: str,
    title: str,
    source_locale: str,
    locale: str,
    outdated: bool,
    edited_at: datetime,
    body: str,
    user_segment_id: Optional[int] = None,
    permission_group_id: Optional[int] = None,
    content_tag_ids: Optional[List[int]] = None,
    label_names: Optional[List[str]] = None,
    outdated_locales: Optional[List[str]] = None,
  ):
    self.id = id
    self.url = url
    self.html_url = html_url
    self.author_id = author_id
    self.comments_disabled = comments_disabled
    self.draft = draft
    self.promoted = promoted
    self.position = position
    self.vote_sum = vote_sum
    self.vote_count = vote_count
    self.section_id = section_id

    self.created_at = created_at
    self.updated_at = updated_at

    self.name = name
    self.title = title
    self.source_locale = source_locale
    self.locale = locale
    self.outdated = outdated

    self.edited_at = edited_at
    self.body = body

    self.user_segment_id = user_segment_id
    self.permission_group_id = permission_group_id
    self.content_tag_ids = content_tag_ids or []
    self.label_names = label_names or []
    self.outdated_locales = outdated_locales or []

  def build_file_name(self) -> str:
    path = urlparse(self.html_url).path
    slug = path.rstrip("/").split("/")[-1]
    return f"{slug}.md"

  def format_content(self) -> str:
    return md(self.body)


class ZendeskArticle:
  @staticmethod
  def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

  @classmethod
  def to_article(cls, content: Dict[str, Any]) -> Article:
    return Article(
      id=content.get("id"),
      url=content.get("url"),
      html_url=content.get("html_url"),
      author_id=content.get("author_id"),
      comments_disabled=content.get("comments_disabled"),
      draft=content.get("draft"),
      promoted=content.get("promoted"),
      position=content.get("position"),
      vote_sum=content.get("vote_sum"),
      vote_count=content.get("vote_count"),
      section_id=content.get("section_id"),

      created_at=cls._parse_datetime(content.get("created_at")),
      updated_at=cls._parse_datetime(content.get("updated_at")),

      name=content.get("name"),
      title=content.get("title"),
      source_locale=content.get("source_locale"),
      locale=content.get("locale"),
      outdated=content.get("outdated"),

      edited_at=cls._parse_datetime(content.get("edited_at")),

      body=content.get("body"),

      user_segment_id=content.get("user_segment_id"),
      permission_group_id=content.get("permission_group_id"),
      content_tag_ids=content.get("content_tag_ids"),
      label_names=content.get("label_names"),
      outdated_locales=content.get("outdated_locales"),
    )