apt-get update
apt-get install -y python-pip
apt-get install -y redis-server
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
apt-get update
apt-get install mongodb-10gen
pip install pymongo
pip install scrapy
pip install redis
pip install numpy
pip intall scrapy-crawlera
