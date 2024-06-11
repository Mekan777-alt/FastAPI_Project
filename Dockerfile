FROM python:3.10-slim-buster AS builder

RUN apt-get update && apt-get install -y postgresql-client dos2unix

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY run.sh .

RUN chmod +x run.sh

RUN dos2unix .env

ENV DBPASSWORD ${DBPASSWORD}

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
