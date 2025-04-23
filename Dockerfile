FROM python:3.11-slim

# Устанавливаем unrar для работы с .rar архивами
RUN apt-get update && \
    apt-get install -y \
    p7zip-full \
    unar && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
