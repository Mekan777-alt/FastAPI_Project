FROM python:3.10-slim-buster AS builder

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN alembic upgrade head

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
