# Getting receipts

## Run the service in a Docker container

To start this service using **Docker Compose** you need:

- create `.evn` file like `.env.example` with appropriate parameters
- run docker-compose

### Standard launch of docker-compose

```shell
docker compose build
docker compose up -d
```

### Run docker-compose using http proxy

```shell
HTTP_PROXY=http://example.org:7777 docker compose build
HTTP_PROXY=http://example.org:7777 docker compose up -d
```

## Using the service

Once started, the service is available on the port `8080`:

```text
http://hostname:8080/docs - Automatic Documentation

http://hostname:8080/get_sms_code - Request an SMS code to the specified phone number
http://hostname:8080/get_session_by_sms_code - Request a session using SMS code
http://hostname:8080/get_receipt - Getting a receipt by QR code (json)
```

Procedure:

1. Request SMS code by phone number (`/get_sms_code`)
2. Activate the session using received SMS code (`/get_session_by_sms_code`)
3. Getting the receipt in json format using the QR code (`/get_receipt`)

After the first activation of the service using the SMS code, you do not need to request the SMS code again until the container is recreated.

The current **refresh token** is stored inside the container in the `/code/default.db` (sqlite) file.

## Run a Python service without a container

### Requirements

Minimum version - **Python 3.10**

### Start order

To start the service you need:

- create `.evn` file like `.env.example` with appropriate parameters
- install dependencies `pip install -r .\requirements.txt`
- run `uvicorn src.main:app --host 0.0.0.0 --port 8080`

### Run tests

To start tests run `python -m pytest -v`
