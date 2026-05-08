from dotenv import load_dotenv
import os
import re

from openai import OpenAI
from pathlib import Path

from src.utils.utils import utils
from storage.base_storage.base_storage import BaseStorage

load_dotenv()

class OpenAiService:
  def __init__(self, storage: BaseStorage):

    self.storage = storage

    self.data = self.storage.get()

    self.client = OpenAI(
      api_key=os.getenv("OPENAI_API_KEY")
    )

    vector_store_id = self.data.open_ai.get("vector_store_id")

    if vector_store_id is None:
      vector_store = self.client.vector_stores.create(
        name=os.getenv("OPENAI_VECTOR_NAME", "default-store")
      )
      self.vector_store_id = vector_store.id
      self.data.open_ai['vector_store_id'] = vector_store.id
      self.data = self.storage.update(self.data)
    else:
      self.vector_store_id = vector_store_id

    assistant_id = self.data.open_ai.get("assistant_id")

    if assistant_id is None:
      assistant = self.client.beta.assistants.create(
        name="OptiBot",
        instructions="""
You are OptiBot, the customer-support bot for OptiSigns.com.
• Tone: helpful, factual, concise.
• Only answer using the uploaded docs.
• Max 5 bullet points; else link to the doc.
• Cite up to 3 "Article URL:" lines per reply.
""",
        model="gpt-4.1",
        tools=[{"type": "file_search"}],
        tool_resources={
          "file_search": {
            "vector_store_ids": [self.vector_store_id]
          }
        }
      )
      self.assistant_id = assistant.id
      self.data.open_ai['assistant_id'] = assistant.id
      self.data = self.storage.update(self.data)
    else:
      self.assistant_id = assistant_id

    
  def _process(self, file_path: str):
    with open(file_path, "rb") as f:
      file = self.client.files.create(
        file=f,
        purpose="assistants"
      )

    vector = self.client.vector_stores.files.create(
      vector_store_id=self.vector_store_id,
      file_id=file.id
    )

    return {
      "path": file_path,
      "file": file,
      "vector": vector
    }

  def process(self, file_path: str):
    paths = self._chunk_markdown(file_path)

    name = os.path.splitext(os.path.basename(file_path))[0]

    print(f"Chunking {name} into {len(paths)} chunks")

    results = []

    for i, path in enumerate(paths):
      try:
        result = utils.retry(lambda: self._process(path))
        results.append(result)
        print(f"Processed chunk {i}")
      except Exception as e:
        print(f"Failed chunk {i}: {e}")
        raise
      finally:
        Path(path).unlink(missing_ok=True)

    print(f"Finish processing {name}")

    return results

  def _chunk_markdown(self, file_path: str, max_size=1000, overlap=200):
    with open(file_path, "r", encoding="utf-8") as f:
      content = f.read()

    sections = re.split(
        r'(?=^#{1,6}\s)|(?=^\d+[\.\)]\s.{50,})',
        content,
        flags=re.MULTILINE
    )

    chunks = []

    for section in sections:
      if not section:
        continue

      if len(section) <= max_size:
        chunks.append(section)
      else:
        start = 0
        while start < len(section):
          chunk = section[start:start + max_size]
          chunks.append(chunk)
          start += max_size - overlap

    file_name = os.path.splitext(os.path.basename(file_path))[0]

    base_dir = Path(file_path).parent
    base_dir.mkdir(parents=True, exist_ok=True)

    paths = []

    for i, chunk in enumerate(chunks):
      path = base_dir / f"{file_name}_{i}.md"
      with open(path, "w", encoding="utf-8") as f:
        f.write(chunk)
      paths.append(str(path))

    return paths