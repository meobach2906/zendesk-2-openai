from pathlib import Path
from utils.utils import utils
from models import schema
from base_storage.base_storage import BaseStorage
import json

class LocalStorage(BaseStorage):
  def __init__(self):
    super().__init__()
    BASE_DIR = Path(__file__).resolve().parent
    self.path = BASE_DIR / "storage" / "storage.json"
    self._storage: schema.Schema = self._load_config()

  def _load_config(self) -> schema.Schema:
    if not self.path.exists():
      return schema.Schema()

    try:
      with open(self.path, "r", encoding="utf-8") as f:
        data = json.load(f)
      return schema.Schema(data)

    except Exception:
      return schema.Schema()
  
  def save(self) -> None:
    payload = json.dumps(self._storage.__dict__, ensure_ascii=False)

    utils.save_file({
      "content": payload,
      "file_path": str(self.path),
    })

  