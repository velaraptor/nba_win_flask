FROM python:3.6

FROM python:3.6

RUN mkdir /app
COPY requirements.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt
COPY . /app

CMD ["python", "get_new_standings.py"]
