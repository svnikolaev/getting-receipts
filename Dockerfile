FROM python:3.11
LABEL maintainer="s.nikolaev@nklv.su"
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/src
COPY ./.env /code/.env
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
