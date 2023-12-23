#! /usr/bin/bash

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
echo | cat hostname=ip-172-31-26-164.ec2.internal | sudo tee -a config.iniecho | cat nodeid=1 | sudo tee -a config.ini

echo | cat [ndbd default] | sudo tee -a config.ini
echo | cat noofreplicas=3
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini

echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-85-112.ec2.internal | sudo tee -a config.ini
echo | cat hostname=ip-172-31-31-228.ec2.internal | sudo tee -a config.ini
echo | cat [ndbd] | sudo tee -a config.ini
echo | cat hostname=ip-172-31-88-166.ec2.internal | sudo tee -a config.ini
echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=4 | sudo tee -a config.ini

echo | cat hostname=ip-172-31-26-111.ec2.internal | sudo tee -a config.iniecho | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini
echo | cat nodeid=5 | sudo tee -a config.ini

echo | cat [mysqld] | sudo tee -a config.ini
echo | cat nodeid=50 | sudo tee -a config.ini
echo | cat hostname=ip-172-31-25-7.ec2.internal | sudo tee -a config.ini
sudo cd /opt/mysqlcluster/home/mysqlc
sudo scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data

sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &