#! /usr/bin/bash

#Installation of sysbench
sudo apt-get install sysbench -y

#Initiation the installation of mysql
sudo service mysqld stop
sudo apt remove mysql-server mysql mysql-devel
sudo mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home
sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc' | sudo tee -a /etc/profile.d/mysqlc.sh
echo 'export PATH=$MYSQLC_HOME/bin:$PATH' | sudo tee -a /etc/profile.d/mysqlc.sh
source /etc/profile.d/mysqlc.sh
sudo apt-get update
sudo apt-get -y install libncurses5

cd "/opt/mysqlcluster/deploy"
sudo mkdir conf 
sudo mkdir mysqld_data 
sudo mkdir ndb_data 
cd conf

echo -e "[mysqld]" | sudo tee -a my.cnf
echo -e "ndbcluster" | sudo tee -a my.cnf
echo -e "datadir=/opt/mysqlcluster/deploy/mysqld_data" | sudo tee -a my.cnf
echo -e "basedir=/opt/mysqlcluster/home/mysqlc" | sudo tee -a my.cnf
echo -e "port=3306" | sudo tee -a my.cnf

echo -e "[ndb_mgmd]" | sudo tee -a config.ini
echo -e "hostname=ip-172-31-20-30.ec2.internal" | sudo tee -a config.ini
echo -e "datadir=/opt/mysqlcluster/deploy/ndb_data" | sudo tee -a config.ini
echo -e "nodeid=1" | sudo tee -a config.ini

echo -e "[ndbd default]" | sudo tee -a config.ini
echo -e "noofreplicas=3" | sudo tee -a config.ini
echo -e "datadir=/opt/mysqlcluster/deploy/ndb_data" | sudo tee -a config.ini

echo -e "[ndbd]" | sudo tee -a config.ini
echo -e "hostname=ip-172-31-26-136.ec2.internal" | sudo tee -a config.ini
echo -e "datadir=/opt/mysqlcluster/deploy/ndb_data" | sudo tee -a config.ini
echo -e "nodeid=2" | sudo tee -a config.ini

echo -e "[ndbd]" | sudo tee -a config.ini
echo -e "hostname=ip-172-31-20-139.ec2.internal" | sudo tee -a config.ini
echo -e "datadir=/opt/mysqlcluster/deploy/ndb_data" | sudo tee -a config.ini
echo -e "nodeid=3" | sudo tee -a config.ini

echo -e "[ndbd]" | sudo tee -a config.ini
echo -e "hostname=ip-172-31-18-70.ec2.internal" | sudo tee -a config.ini
echo -e "datadir=/opt/mysqlcluster/deploy/ndb_data" | sudo tee -a config.ini
echo -e "nodeid=4" | sudo tee -a config.ini

echo -e "[mysqld]" | sudo tee -a config.ini
echo -e "nodeid=50" | sudo tee -a config.ini

sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/

sudo cd /opt/mysqlcluster/home/mysqlc
sudo scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data
