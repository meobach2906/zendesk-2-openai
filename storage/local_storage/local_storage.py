from pathlib import Path
from utils.utils import utils
from models import schema
from base_storage.base_storage import BaseStorage
import json

class LocalStorage(BaseStorage):
  def __init__(self):
    BASE_DIR = Path(__file__).resolve().parent
    self.path = BASE_DIR / "storage" / "storage.json"
    self.storage: schema.Schema = self._init_load()

  def _init_load(self):
    with open(self.path, "r", encoding="utf-8") as f:
      data = json.load(f)
    return schema.Schema(data)
  
  def save(self):
    utils.save_file(json.dumps(self.storage.__dict__), self.path)

  