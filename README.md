This repository is for LOG8415E final assignment (Scaling Databases and Implementing Cloud Design Patterns) edited by ZAKARIA HANIRI.

To run the code, you need to:
- Install python 3 or above before.
- Upgrade pip before.
- Have an AWS account before ( It is necessary to have your credentials: access_key_id,secret_access_key,session_token)
- Once you have all of this, you have to copy past your credentials in the script.sh file
- Then you will run the code Setup_Benchmark_standalone.py in which you will create the
stand-alone ec2 instance, install mysql, sakila database and sysbench in it, then perform the
sysbench benchmark.
- Then you will run the code Setup_Benchmark_cluster.py in which you will create the mysql
cluster ec2 instances (1 master and 3 slaves), perform on the master the installation and
configuration of mysql, installation of sakila database and sysbench, perform on the slaves
the installation and configuration of mysql and the installation of sysbench, then perform the
sysbench benchmark of the cluster.
- Then you will run the code SetupANDsend_request_proxy.py in which you will create an ec2
instance of the proxy, and specify and send your SQL requests to the proxy with giving it the
proxy mode (direct hit, random, customize) in order to route your request to the appropriate
cluster node depending on the specified mode.
- Then you will run the code SetupANDsend_request_gatekeeper.py in which you will create 2
ec2 instances of gatekeeper and trusted host, then specify and send your SQL requests to the
gatekeeper with giving it the proxy mode (direct hit, random, customize) in order to check
and validate it, and then if it is authorized, it will redirect it to the trusted host with the
given proxy mode . Once the trusted host receives it, it will send it to the proxy with the
givent proxy mode .
