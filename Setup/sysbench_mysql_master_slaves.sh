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

deploy_cluster="/opt/mysqlcluster/deploy"
cnf_cluster="/opt/mysqlcluster/deploy/conf"

cd "$deploy_cluster"
sudo mkdir conf mysqld_data ndb_data 
cd "$conf_cluster"

echo | cat [mysqld] | sudo tee -a my.cnf
echo | cat ndbcluster | sudo tee -a my.cnf
echo | cat datadir=/opt/mysqlcluster/deploy/mysqld_data | sudo tee -a my.cnf
echo | cat basedir=/opt/mysqlcluster/home/mysqlc | sudo tee -a my.cnf
echo | cat port=3306 | sudo tee -a my.cnf

echo | cat [ndb_mgmd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-19-213.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=1 | sudo tee -a config.ini

echo | cat [ndbd default] | sudo tee -a config.ini
echo | cat noofreplicas=3
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini

echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-24-91.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=2 | sudo tee -a config.ini

echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-30-192.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=3 | sudo tee -a config.ini

echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-18-52.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=4 | sudo tee -a config.ini

echo | cat [mysqld] | sudo tee -a config.ini
echo | cat nodeid=50 | sudo tee -a config.ini

sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/

sudo cd /opt/mysqlcluster/home/mysqlc
sudo scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data

sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &
