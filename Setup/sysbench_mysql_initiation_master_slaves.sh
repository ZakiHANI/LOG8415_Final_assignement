#! /usr/bin/bash

#Installation of sysbench
sudo apt-get install sysbench -y

#Initiation the installation of mysql
sudo service mysqld stop
sudo apt remove mysql-server mysql mysql-devel

home_cluster="/opt/mysqlcluster/home"

sudo mkdir -p "$home_cluster"
cd "$home_cluster"
sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

echo 'export MYSQLC_HOME='"$home_cluster"'/mysqlc' | sudo tee -a /etc/profile.d/mysqlc.sh
echo 'export PATH=$MYSQLC_HOME/bin:$PATH' | sudo tee -a /etc/profile.d/mysqlc.sh

source /etc/profile.d/mysqlc.sh
sudo apt-get update
sudo apt-get -y install libncurses5
