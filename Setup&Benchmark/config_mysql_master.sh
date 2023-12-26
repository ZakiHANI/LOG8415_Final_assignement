#! /usr/bin/bash

sudo mkdir -p /opt/mysqlcluster/deploy
sudo mkdir -p /opt/mysqlcluster/home/mysqlc
cd /opt/mysqlcluster/deploy
sudo mkdir -p conf
sudo mkdir -p mysqld_data
sudo mkdir -p ndb_data
sudo chmod +w ./conf
echo | cat LOG8415_Final_assignement/Setup/mycnf | sudo tee conf/my.cnf
echo | cat LOG8415_Final_assignement/Setup/configini.txt | sudo tee conf/config.ini
