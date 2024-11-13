# Базовый образ
FROM python:3.9

# Установка рабочей директории
WORKDIR /app

# Копирование файлов
COPY . /app

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Открытие порта
EXPOSE 8501

# Команда запуска
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

