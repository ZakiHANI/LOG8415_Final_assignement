#Installation of sakila
sakila_dir='home/sak'
sudo mkdir "$sakila_dir"
cd "$sakila_dir"
sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz
sudo  tar xvf sakila-db.tar.gz

mysql -u root -e "SOURCE /home/sak/sakila-db/sakila-schema.sql;"
mysql -u root -e "SOURCE /home/sak/sakila-db/sakila-data.sql;"

mysql -u root -e "USE sakila; SHOW FULL TABLES;"
mysql -u root -e "USE sakila; SELECT COUNT(*) FROM film;"

mysql -u root -e "GRANT ALL PRIVILEGES ON sakila.* TO 'root'@'%' IDENTIFIED BY '' WITH GRANT OPTION;"
mysql -u root -e "FLUSH PRIVILEGES"
