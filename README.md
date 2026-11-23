\# Async Deflate Compression API



Веб-приложение с HTTP API для асинхронного сжатия файлов

по алгоритму Deflate (Gzip). Вариант №14.



\## Общее описание



Проект состоит из трёх этапов:



1\. Утилита командной строки для сжатия файлов Deflate.

2\. HTTP API на `BaseHttpRequestHandler` с файловым хранилищем.

3\. HTTP API с хранилищем на SQLite через ponyORM.



\## Функции и настройки



\### CLI



`python -m src.cli INPUT OUTPUT`



\- `INPUT` — путь к файлу для сжатия.

\- `OUTPUT` — путь к результирующему `.gz`-файлу.



\### HTTP API



Маршруты перечислены в таблице 14 сборника вариантов.

Обязательные заголовки запросов:



\- `Content-Type: application/json` (POST, PUT, PATCH) — иначе 415.

\- `Accept: application/json` — иначе 406.

\- `Accept-Language: en` — иначе 406.



\### Переменные окружения



\- `TEST\_MODE=1` — запуск без реального сжатия (заглушка).

\- `API\_PORT` — порт сервера, по умолчанию 8080.

\- `STORAGE\_DIR` — каталог файлового хранилища.



\## Сборка и запуск тестов



```bash

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt



./run.sh server

./run.sh test

./run.sh lint

./run.sh coverage

