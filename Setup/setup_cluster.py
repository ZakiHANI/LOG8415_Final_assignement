import configparser
import boto3
from functions import *
import paramiko
import base64
import os
import json
from threading import Thread
import re

if __name__ == '__main__':
    # Get credentials from the config file :
    path = os.path.dirname(os.getcwd())
    config_object = configparser.ConfigParser()
    with open(path+"/my_credentials.ini","r") as file_object:
        #Loading of the aws tokens
        config_object.read_file(file_object)
        key_id = config_object.get("resource","aws_access_key_id")
        access_key = config_object.get("resource","aws_secret_access_key")
        session_token = config_object.get("resource","aws_session_token")
        ami_id = config_object.get("ami","ami_id")


    print('============================>The begining of setup')

    #--------------------------------------ec2 resource and client creations----------------------------------------
    
    #Create ec2 resource with our credentials:
    ec2_serviceresource = resource_ec2(key_id, access_key, session_token)
    print("============> Successful creation of ec2 resource <=================")
    #Create ec2 client with our credentials:
    ec2_serviceclient = client_ec2(key_id, access_key, session_token)
    print("============> Successful creation of ec2 client <=================")

    #--------------------------------------keypair creation or check of prior existance-----------------------------------
    
    key_pair_name = create_keypair('final_keypair', ec2_serviceclient)

    #---------------------------------------------------Get default VPC ID-----------------------------------------------------
    #Get default vpc description : 
    default_vpc = ec2_serviceclient.describe_vpcs(
        Filters=[
            {'Name':'isDefault',
             'Values':['true']},
        ]
    )
    default_vpc_desc = default_vpc.get("Vpcs")
   
    # Get default vpc id : 
    vpc_id = default_vpc_desc[0].get('VpcId')


    #--------------------------------------Try create a security group--------------------------------
  
    try:
        security_group_id = create_security_group("sec_group","final_security_group",vpc_id,ec2_serviceresource)  
    
    except :
        #Get the standard security group from the default VPC :
        sg_dict = ec2_serviceclient.describe_security_groups(Filters=[
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc_id,
                ]
            },

        {
                'Name': 'group-name',
                'Values': [
                    "final_security_group",
                ]
            },

        ])

        security_group_id = (sg_dict.get("SecurityGroups")[0]).get("GroupId")
    

    #--------------------------------------Pass sysbench and mysqlinstallation script for master and slaves script into the user_data parameter ------------------------------
    with open('sysbench_mysql_master_slaves.sh', 'r') as f :
        sysbench_mysql_master_slaves = f.read()

    sysbench_mysql = str(sysbench_mysql_master_slaves)

    #--------------------------------------Create Instances of master and slaves with installing sysbench and mysql on them ------------------------------------------------------------

    # Create master t2.micro instance:
    instance_type = "t2.micro"
    
    print("\n Creating instance : master ")
    # Creation of the master
    master_t2= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,['us-east-1a'],"master",sysbench_mysql)
    print("\n master created successfully with installation of sysbench and mysql")

    print("\n Creating instances : slaves ")
    # Creation of the slaves
    slaves_t2= create_instance_ec2(3,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,['us-east-1a','us-east-1a','us-east-1a'],"slave",sysbench_mysql)
    print("\n slaves created successfully with installation of sysbench and mysql")

    #--------------------------------------Update ip addresses of master and slaves in mysql_config_master file------------------------------------------------------------

    # line17='echo | cat hostname='+str(master_t2[0][1])+' | sudo tee -a config.ini'
    # line25='echo | cat hostname='+str(slaves_t2[0][1])+' | sudo tee -a config.ini'
    # line31='echo | cat hostname='+str(slaves_t2[1][1])+' | sudo tee -a config.ini'
    # line36='echo | cat hostname='+str(slaves_t2[2][1])+' | sudo tee -a config.ini'
    # ubdate_ip_addresss_master('mysql_config_master.sh',16,line17)
    # ubdate_ip_addresss_master('mysql_config_master.sh',24,line25)
    # ubdate_ip_addresss_master('mysql_config_master.sh',30,line31)
    # ubdate_ip_addresss_master('mysql_config_master.sh',35,line36)



    # from functions import *
    # ubdate_ip_addresss_master('mysql_config_master.sh',[8],['ppp'])
    print("\n Ip addresses of master and slaves are updated successfully in mysql config master file....")
    

    #--------------------------------------Config mysql on master ------------------------------------------------------------
    print(master_t2)
    print("\n Configuration of mysql on master....")
    publicIpAddress_master=master_t2[0][3]
    ssh_master = paramiko.SSHClient()
    ssh_master.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_master = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_master.connect(hostname=publicIpAddress_master,username='ubuntu', pkey=key_private_master)
    ssh_master.exec_command('sudo apt-get update')
    in_,out_,err_=ssh_master.exec_command('sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
    print('out_:', out_.read())
    print('err_:', err_.read())
                                          
    in_,out_,err_=ssh_master.exec_command('sudo bash LOG8415_Final_assignement/Setup/mysql_config_master.sh')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command('sudo deploy_cluster="/opt/mysqlcluster/deploy" && sudo cnf_cluster="/opt/mysqlcluster/deploy/conf"')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command('sudo cd "/opt/mysqlcluster/deploy" && sudo mkdir conf mysqld_data ndb_data && sudo cd "/opt/mysqlcluster/deploy/conf"')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command(' echo | cat [mysqld] | sudo tee -a my.cnf && echo | cat ndbcluster | sudo tee -a my.cnf')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command(' echo | cat datadir=/opt/mysqlcluster/deploy/mysqld_data | sudo tee -a my.cnf && echo | cat basedir=/opt/mysqlcluster/home/mysqlc | sudo tee -a my.cnf')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command(' echo | cat port=3412 | sudo tee -a my.cnf && echo | cat [ndb_mgmd] | sudo tee -a config.ini')
    print('out_:', out_.read())
    print('err_:', err_.read())
        
    #Private dns name master
    master_pv_dns='echo | cat hostname='+str(master_t2[0][1])+' | sudo tee -a config.ini'
    in_,out_,err_=ssh_master.exec_command(master_pv_dns)
    print('out_:', out_.read())
    print('err_:', err_.read())

    in_,out_,err_=ssh_master.exec_command(' echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini && echo | cat nodeid=1 | sudo tee -a config.ini')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command(' echo | cat [ndbd default] | sudo tee -a config.ini && echo | cat noofreplicas=3 ')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command(' echo | cat [ndbd] | sudo tee -a config.ini && echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini ')
    print('out_:', out_.read())
    print('err_:', err_.read())
    
    #Private dns name slave 1
    slave1_pv_dns='echo | cat hostname='+str(slaves_t2[0][1])+' | sudo tee -a config.ini'
    in_,out_,err_=ssh_master.exec_command(slave1_pv_dns)
    print('out_:', out_.read())
    print('err_:', err_.read())

    in_,out_,err_=ssh_master.exec_command(' echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini && echo | cat nodeid=2 | sudo tee -a config.ini && echo | cat [ndbd] | sudo tee -a config.ini ')
    print('out_:', out_.read())
    print('err_:', err_.read())

    #Private dns name slave 2
    slave2_pv_dns='echo | cat hostname='+str(slaves_t2[1][1])+' | sudo tee -a config.ini'
    in_,out_,err_=ssh_master.exec_command(slave2_pv_dns)
    print('out_:', out_.read())
    print('err_:', err_.read())
    
    in_,out_,err_=ssh_master.exec_command(' echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini && echo | cat nodeid=3 | sudo tee -a config.ini && echo | cat [ndbd] | sudo tee -a config.ini ')
    print('out_:', out_.read())
    print('err_:', err_.read())


    #Private dns name slave 3
    slave3_pv_dns='echo | cat hostname='+str(slaves_t2[2][1])+' | sudo tee -a config.ini'
    in_,out_,err_=ssh_master.exec_command(slave3_pv_dns)
    print('out_:', out_.read())
    print('err_:', err_.read())
    
    in_,out_,err_=ssh_master.exec_command(' echo | cat datadir=/opt/mysqlcluster/deploy/ndb_data | sudo tee -a config.ini && echo | cat nodeid=4 | sudo tee -a config.ini ')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command(' echo | cat [mysqld] | sudo tee -a config.ini && echo | cat nodeid=50 | sudo tee -a config.ini ')
    print('out_:', out_.read())
    print('err_:', err_.read())

    time.sleep(50)
    in_,out_,err_=ssh_master.exec_command("/opt/mysqlcluster/home/mysqlc/bin/mysql -h 127.0.0.1 -u root < /home/ubunto/LOG8415_Final_assignement/Setup/mysql_user.sql")
    print('out_:', out_.read())
    print('err_:', err_.read())

    print("\n mysql config on master has been made successfully....")

    # #--------------------------------------Config mysql on slaves ------------------------------------------------------------
    # print("\n Configuration of mysql on slaves....")
    # for i in range (3):
    #     publicIpAddress_slave=slaves_t2[i][3]
    #     ssh_slave = paramiko.SSHClient()
    #     ssh_slave.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     key_private_slave = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    #     ssh_slave.connect(hostname=publicIpAddress_slave,username='ubuntu', pkey=key_private_master)
    #     ssh_slave.exec_command('sudo apt-get update && sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
    #     in_,out_,err_=ssh_slave.exec_command('sudo bash \home\ubunto\Final_Project\LOG8415_Final_assignement\Setup\mysql_config_slaves.sh')
    #     print('out_:', out_.read())
    #     print('err_:', err_.read())

    # print("\n mysql configs on slaves has been made successfully....")
    #--------------------------------------Installing sakila on master  ------------------------------------------------------------
    print("\n Installation of sakila on master....")

    ssh_master = paramiko.SSHClient()
    ssh_master.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_master = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_master.connect(hostname=publicIpAddress_master,username='ubuntu', pkey=key_private_master)
    ssh_master.exec_command('sudo apt-get update && sudo  mkdir home/sak && cd home/sak')
    ssh_master.exec_command('sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz && sudo  tar xvf sakila-db.tar.gz')
    in_,out_,err_=ssh_master.exec_command(' mysql SOURCE /home/sak/sakila-db/sakila-schema.sql &&  mysql SOURCE /home/sak/sakila-db/sakila-data.sql')
    print('out_:', out_.read())
    print('err_:', err_.read())

    print("\n Sakila installation on master has been made successfully....")

    #--------------------------------------Installing sakila on slaves ------------------------------------------------------------
    # print("\n Installation of sakila on slaves....")

    # for i in range (3):
    #     publicIpAddress_slave=slaves_t2[i][1]
    #     ssh_slave = paramiko.SSHClient()
    #     ssh_slave.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     key_private_slave = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    #     ssh_slave.connect(hostname=publicIpAddress_slave,username='ubuntu', pkey=key_private_master)
    #     ssh_slave.exec_command('sudo apt-get update && sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
    #     in_,out_,err_=ssh_slave.exec_command('sudo bash \home\ubunto\Final_Project\LOG8415_Final_assignement\Setup\sakila_master_slaves.sh')
    #     print('out_:', out_.read())
    #     print('err_:', err_.read())

    # print("\n Sakila installation on slaves has been made successfully....")


    print('============================>SETUP ends')

    