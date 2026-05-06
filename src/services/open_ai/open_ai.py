from dotenv import load_dotenv
import os

from openai import OpenAI

from utils.utils import utils

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
      "file": file,
      "vector": vector
    }
  
  def process(self, file_path):
    return utils.retry(self._process(file_path))


