docker run -d --name telegram_mongo -p 127.0.0.1:27017:27017 -v /nick/mongo_db:/data/db mongo:latest
docker run -d -p 0.0.0.0:4242:8888 -t --name inote --link telegram_mongo:mongo -e "PASSWORD=test" ipython/notebook
docker exec -it inote bash
pip2.7 install pymongo
exit
