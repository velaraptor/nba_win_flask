FROM python:3.6

RUN mkdir /app
COPY requirements.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt
COPY . /app
COPY nba_win.db /var/data/
CMD ["python", "fetch_standings.py"]
