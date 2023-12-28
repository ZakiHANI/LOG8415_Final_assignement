#! /usr/bin/bash

sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home
sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

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

sudo mkdir -p /opt/mysqlcluster/deploy/ndb_data
sudo /opt/mysqlcluster/home/mysqlc/bin/ndbd -c ec2-54-85-81-113.compute-1.amazonaws.com:1186

