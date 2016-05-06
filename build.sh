sudo apt-get install -y python-dev python-pip libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev
apt-get install -y redis-server
apt-get install -y mongodb
pip install pymongo
pip install zope.interface
pip install cryptography
pip install Scrapy
pip install redis
#pip install numpy
pip install scrapy-crawlera

#redis setting
sed -i 's/bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf
service redis-server restart

#mongodb setting
sed -i 's/bind_ip = 127.0.0.1/bind_ip = 0.0.0.0/g' /etc/mongodb.conf
service mongodb restart
