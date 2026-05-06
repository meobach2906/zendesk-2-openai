from abc import ABC, abstractmethod
from models import schema

class BaseStorage(ABC):
  def __init__(self):
    self.storage = schema.Schema()

  @abstractmethod
  def save(self):
    pass

  def update(self, data):
    self.storage = schema.Schema(data)
    self.save()

  def get(self):
    return self.storage
    

