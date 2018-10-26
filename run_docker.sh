

docker logs nba_api &>> logs/nba_api.log
docker logs web_app &>> logs/web_app.log
docker-compose build
docker-compose up -d
