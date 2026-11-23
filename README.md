# Async Deflate Compression API

Веб-приложение с HTTP API для асинхронного сжатия файлов
по алгоритму Deflate (Gzip). Вариант №14.

## Общее описание

Проект состоит из трёх этапов:

1. Утилита командной строки для сжатия файлов Deflate.
2. HTTP API на `BaseHttpRequestHandler` с файловым хранилищем.
3. HTTP API с хранилищем на SQLite через `ponyORM`.

## Функции и настройки

### CLI

`py -m src.cli INPUT OUTPUT`

- `INPUT` — путь к файлу для сжатия.
- `OUTPUT` — путь к результирующему `.gz`-файлу.

### HTTP API

Маршруты перечислены в таблице 14 сборника вариантов.
Обязательные заголовки запросов:

- `Content-Type: application/json` (POST, PUT, PATCH) — иначе 415.
- `Accept: application/json` — иначе 406.
- `Accept-Language: en` — иначе 406.

### Переменные окружения

- `TEST_MODE=1` — запуск без реального сжатия (заглушка).
- `API_PORT` — порт сервера, по умолчанию 8080.

## Сборка и запуск тестов

```bash
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt

py -m src.server
py -m pytest tests -v