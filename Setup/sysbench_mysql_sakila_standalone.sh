
sudo apt-get update -y

#Installation of mysql
sudo apt-get install mysql-server -y
sudo apt-get install sysbench -y

sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz
sudo  tar xvf sakila-db.tar.gz

mysql -u root -e "SOURCE /sakila-db/sakila-schema.sql;"
mysql -u root -e "SOURCE /sakila-db/sakila-data.sql;"

mysql -e "CREATE USER 'me'@'localhost' IDENTIFIED BY 'ZAKARIA';"
mysql -e "GRANT ALL PRIVILEGES on sakila.* TO 'me'@'localhost';"
