FROM python:3.6

RUN mkdir /app
COPY requirements.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt
COPY . /app
CMD ["python", "fetch_raw_standings.py"]
