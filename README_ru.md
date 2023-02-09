# Получение чеков

## Запуск сервиса в Docker контейнере

Чтобы запустить сервис c использованием **Docker Compose** нужно:

- создать `.evn` файл, по примеру `.env.example` с соответствующими параметрами
- выполнить запуск docker-compose

### Стандартный запуск docker-compose

```shell
docker compose build
docker compose up -d
```

### Запуск docker-compose с использованием http proxy

```shell
HTTP_PROXY=http://example.org:7777 docker compose build
HTTP_PROXY=http://example.org:7777 docker compose up -d
```

## Использование сервиса

После включения сервис доступен на порту `8080`:

```text
http://hostname:8080/docs - Автоматическая документация

http://hostname:8080/get_sms_code - Запрос SMS-кода на указанный номер телефона
http://hostname:8080/get_session_by_sms_code - Запрос сессии с помощью SMS-кода
http://hostname:8080/get_receipt - Получение чека по QR-коду (json)
```

Порядок действий:

1. По номеру телефона запрашивается СМС-код (`/get_sms_code`)
2. С помощью полученого СМС-кода активируется сессия (`/get_session_by_sms_code`)
3. С помощью QR-кода получается чек в формате json (`/get_receipt`)

После первой активации сервиса с помощью СМС-кода заново запрашивать СМС-код не нужно до пересоздания контейнера.

Текущий **refresh token** хранится внутри контейнера в файле `/code/default.db` (sqlite).

## Запуск Python сервиса без контейнера

### Требования

Минимальная версия - **Python 3.10**

### Порядок запуска

Чтобы запустить сервис нужно:

- создать `.evn` файл, по примеру `.env.example` с соответствующими параметрами
- установить зависимости `pip install -r .\requirements.txt`
- выполнить `uvicorn src.main:app --host 0.0.0.0 --port 8080`

### Запуск тестов

Чтобы запустить тесты выполните `python -m pytest -v`
