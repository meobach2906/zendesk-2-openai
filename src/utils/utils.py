import time
from pathlib import Path

class Utils:
  def save_file(self, data):
    content = data.get('content')
    file_path = data.get('file_path')
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
      f.write(content)
    return file_path
  
  def retry(self, func, retry_attempt = 3, wait_time = 5):
    retry_times = 0
    while retry_times < retry_attempt:
      try:
        return func()
      except Exception as e:
        retry_times += 1
        print(f"Failed attempt {retry_times}: {e}")

        if retry_times >= retry_attempt:
          raise

        time.sleep(wait_time)

utils = Utils()