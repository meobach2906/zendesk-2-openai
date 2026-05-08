from abc import ABC, abstractmethod
from storage.models import schema
from typing import Any

class BaseStorage(ABC):
  def __init__(self):
    self._storage = schema.Schema()

  @abstractmethod
  def save(self) -> None:
    pass

  def update(self, data: Any) -> schema.Schema:
    self._storage = schema.Schema(data)
    self.save()
    return self._storage

  def get(self) -> schema.Schema:
    return self._storage