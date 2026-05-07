from dotenv import load_dotenv
import os

from storage.local_storage.local_storage import LocalStorage
from storage.digital_ocean_space_storage.digital_ocean_space_storage import DigitalOceanSpaceStorage

from src.crawlers.optisign.crawlers.crawler import Crawler
from src.services.open_ai.open_ai import OpenAiService

load_dotenv()

STORAGE = os.getenv("STORAGE") or 'local'

STORAGE = STORAGE.lower()

def init_storage(storage):
  if storage == 'local':
    return LocalStorage()
  if storage == 'digital_ocean_storage':
    return DigitalOceanSpaceStorage()
  raise ValueError(f"Unknown storage type: {storage}")

def main():
  storage_type = os.getenv("STORAGE", "local").lower()

  storage = init_storage(storage_type)

  openai_service = OpenAiService(storage)

  crawler = Crawler(storage, openai_service)

  crawler.start()


if __name__ == "__main__":
  main()