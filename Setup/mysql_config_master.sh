#! /usr/bin/bash

deploy_cluster="/opt/mysqlcluster/deploy"
5545150Yes
cnf_cluster="/opt/mysqlcluster/deploy/conf"
Yes2hellohello
sudo mkdir -p "$deploy_cluster"
cd "$deploy_cluster"
sudo mkdir conf mysqld_data ndb_data 
cd "$conf_cluster"

echo | cat [mysqld] | sudo tee -a my.cnf
echo | cat ndbcluster | sudo tee -a my.cnf
echo | cat datadir=/opt/mysqlcluster/deploy/mysqld_data | sudo tee -a my.cnf
echo | cat basedir=/opt/mysqlcluster/home/mysqlc | sudo tee -a my.cnf
echo | cat port=3306 | sudo tee -a my.cnf

echo | cat [ndb_mgmd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-92-72.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=1 | sudo tee -a config.ini

echo | cat [ndbd default] | sudo tee -a config.ini
echo | cat noofreplicas=3
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini

echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-85-112.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=3 | sudo tee -a config.ini

echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-88-166.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=4 | sudo tee -a config.ini

echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-86-179.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=5 | sudo tee -a config.ini

echo | cat [mysqld] | sudo tee -a config.ini
echo | cat nodeid=50 | sudo tee -a config.ini

sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/

sudo cd /opt/mysqlcluster/home/mysqlc
sudo scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data

sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &