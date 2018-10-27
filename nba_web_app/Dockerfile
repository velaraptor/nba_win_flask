FROM python:3.6

RUN mkdir /app
COPY requirements.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt
COPY . /app

ENTRYPOINT ["python"]
CMD ["nba_win.py"]