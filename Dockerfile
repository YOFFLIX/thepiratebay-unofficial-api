FROM python:3.8-slim-buster

COPY . /app
COPY ./requirements.txt /app

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /code

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--reload"]
