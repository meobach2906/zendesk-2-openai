FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=""
ENV OPENAI_VECTOR_NAME=""
ENV STORAGE="local"
ENV ZENDESK_BASE_URL=""
ENV BUCKET=""
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""

CMD ["python", "main.py"]