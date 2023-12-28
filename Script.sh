#!/bin/bash

# Clone the git repository for the assignement 
git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git

cd LOG8415_Final_assignement
# Enter the AWS credentials here
new_aws_access_key="key"
new_aws_secret_key="secret"
new_aws_token_key="token"

# Fill in the credentials.ini file with entered aws_access_key
sed -i "s#aws_access_key_id=.*#aws_access_key_id=${new_aws_access_key}#" my_credentials.ini

# Fill in the credentials.ini file with entered new_aws_secret_key
sed -i "s#aws_secret_access_key=.*#aws_secret_access_key=${new_aws_secret_key}#" my_credentials.ini

# Fill in the credentials.ini file with entered new_aws_token_key
sed -i "s#aws_session_token=.*#aws_session_token=${new_aws_token_key}#" my_credentials.ini

# Install requirements
pip install boto3
pip install paramiko
pip install configparser
pip install ping3

# Open the folder of setup and benchmarking
cd SetupANDBenchmark

#Execute Setup and sysbench benchmark of standalone
python3 Setup_Benchmark_standalone.py

'In this code you will create the stand-alone ec2 instance, install mysql, sakila database and sysbench in it,
 then perform the sysbench benchmark.'


#Execute Setup and sysbench benchmark of mysql cluster
python3 Setup_Benchmark_cluster.py

'In this code you will :
- Create the mysql cluster ec2 instances (1 master and 3 slaves)
- Perform on the master the installation and configuration of mysql, installation of sakila database and sysbench. 
- Perform on the slaves the installation and configuration of mysql and the installation of sysbench.
- Then perform the sysbench benchmark of the clustaer.' 

cd ..
# Open the folder of the proxy
cd Proxy

#Execute Sending requests to the proxy
python3 SetupANDsend_request_proxy.py

'In this code you will create an ec2 instance of the proxy, and specify and send your SQL requests to the proxy with giving it the proxy mode (direct hit, random, customize)
in order to rout your request to the appropriate cluster node depending on the specified mode.'


cd ..
# Open the folder of the Gatekeeper
cd Proxy

#Execute Sending requests to the proxy
python3 SetupANDsend_request_gatekeeper.py

'In this code you will specify create 2 ec2 instances of gatekeeper and trusted host, then specify and send your SQL requests to the gatekeeper with 
giving it the proxy mode (direct hit, random, customize) in order to check and validate it, and then if it is authorized, it will redirect it 
to the trusted host with the given proxy mode . Onece the trusted host receives it, it will send it to the proxy with the givent proxy mode .'
