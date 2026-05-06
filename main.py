from dotenv import load_dotenv
import os

from storage.local_storage.local_storage import LocalStorage
from storage.digital_ocean_space_storage.digital_ocean_space_storage import DigitalOceanSpaceStorage

from src.crawlers.optisign.crawlers.crawler import Crawler
from src.services.open_ai.open_ai import OpenAiService

load_dotenv()

STORAGE = os.getenv("STORAGE") or 'local'

STORAGE = STORAGE.lower()

def initStorage(storage):
  if storage == 'local':
    return LocalStorage()
  if storage == 'digital_ocean_storage':
    return DigitalOceanSpaceStorage()
  
crawler = Crawler(initStorage(STORAGE), OpenAiService())

crawler.start()