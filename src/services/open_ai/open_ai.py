from dotenv import load_dotenv
import os

from openai import OpenAI

from utils.utils import utils
from pathlib import Path

import re

class OpenAiService:
  def __init__(self):
    self.client = OpenAI(api_key=os.get('OPENAI_API_KEY'))

    self.vector_store = self.client.vector_stores.create(name=os.get('OPENAI_VECTOR_NAME'))

    self.assistant = self.client.beta.assistants.create(
      name="OptiBot",
      instructions="""You are OptiBot, the customer-support bot for OptiSigns.com.
        • Tone: helpful, factual, concise.
        • Only answer using the uploaded docs.
        • Max 5 bullet points; else link to the doc.
        • Cite up to 3 "Article URL:" lines per reply.""",
      model="gpt-4.1",
      tools=[{"type": "file_search"}],
      tool_resources={
          "file_search": {
              "vector_store_ids": [self.vector_store.id]
          }
      }
    )

  def _process(self, file_path):
    file = self.client.files.create(
      file=open(file_path, "rb"),
      purpose="assistants"
    )
    vector = self.client.vector_stores.files.create(
      vector_store_id=self.vector_store.id,
      file_id=file.id
    )
    return {
      "path": file_path,
      "file": file,
      "vector": vector
    }
  
  def process(self, file_path):
    paths = self._chunk_markdown(file_path)

    results = []
    for path in paths:
      result = utils.retry(self._process(path))
      results.append(result)

    return results
  
  def _chunk_markdown(self, file_path, max_size=1000, overlap=200):

    with open(file_path, "r", encoding="utf-8") as f:
      content = f.read()

    sections = re.split(r'(?=^#{1,2} )', content, flags=re.MULTILINE)

    chunks = []

    for section in sections:
      if len(section) <= max_size:
        chunks.append(section)
      else:
        start = 0
        while start < len(section):
          end = start + max_size
          chunk = section[start:end]
          chunks.append(chunk)
          start += max_size - overlap

    name = os.path.splitext(os.path.basename(file_path))[0]

    paths = []
    for i, chunk in enumerate(chunks):
      path = f"{Path(__file__).resolve().parent}/public/{name}_{i}.md"
      with open(path, "w") as f:
        f.write(chunk)
      paths.append(path)

    return paths

