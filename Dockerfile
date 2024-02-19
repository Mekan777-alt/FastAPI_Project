
# Используем официальный образ Python в качестве родительского
FROM python:3.10-slim-buster AS builder

RUN apt-get update && apt-get install -y postgresql-client

# Копируем только файл requirements.txt
COPY requirements.txt .

# Устанавливаем необходимые зависимости
RUN pip install -r requirements.txt

# Копируем содержимое текущей директории в контейнер в /app
COPY . .

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Запускаем приложение при запуске контейнера
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
