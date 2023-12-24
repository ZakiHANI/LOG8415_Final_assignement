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

sudo tee -a config.ini <<EOF
[ndb_mgmd]
hostname=ip-172-31-20-195.ec2.internal
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=3
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=ip-172-31-17-15.ec2.internal
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=3

[ndbd]
hostname=ip-172-31-17-172.ec2.internal
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=4

[ndbd]
hostname=ip-172-31-20-187.ec2.internal
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=5

[mysqld]
nodeid=50
EOF

[mysqld]

sudo tee -a my.cnf <<EOF
[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306
EOF

sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/

sudo cd /opt/mysqlcluster/home/mysqlc
sudo scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data
