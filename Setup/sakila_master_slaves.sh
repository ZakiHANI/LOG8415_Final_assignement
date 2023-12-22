#Installation of sakila
sakila_dir='home/sak'
sudo mkdir "$sakila_dir"
cd "$sakila_dir"
sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz
sudo  tar xvf sakila-db.tar.gz

sudo mysql SOURCE /home/sak/sakila-db/sakila-schema.sql;
sudo mysql SOURCE /home/sak/sakila-db/sakila-data.sql;