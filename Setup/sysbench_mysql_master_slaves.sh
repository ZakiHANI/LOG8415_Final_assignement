#! /usr/bin/bash

# sudo service mysqld stop
# sudo apt remove mysql-server mysql mysql-devel
sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home
wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc'  > /etc/profile.d/mysqlc.sh
echo 'export PATH=$MYSQLC_HOME/bin:$PATH'  >> /etc/profile.d/mysqlc.sh

source /etc/profile.d/mysqlc.sh
sudo apt-get update
sudo apt-get -y install libncurses5


sudo mkdir -p /opt/mysqlcluster/deploy
sudo mkdir -p /opt/mysqlcluster/home/mysqlc
cd /opt/mysqlcluster/deploy
sudo mkdir -p conf
sudo mkdir -p mysqld_data
sudo mkdir -p ndb_data
sudo chmod +w ./conf
echo | cat LOG8415_Final_assignement/Setup/mycnf | sudo tee conf/my.cnf
echo | cat LOG8415_Final_assignement/Setup/configini.txt | sudo tee conf/config.ini
