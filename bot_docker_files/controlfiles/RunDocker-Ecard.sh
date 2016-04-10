./RunMongo.sh
docker run -i -t -a STDOUT --link telegram_mongo:mongo -v /home/nick/PycharmProjects/E-Card:/bot --name e-card nickveld/e-card_bot:latest