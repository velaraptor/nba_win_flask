FROM python:3.6

COPY . /app
WORKDIR /app
COPY nba_win.db /var/data/
RUN pip install -r requirements.txt
CMD ["python", "fetch_standings.py"]
