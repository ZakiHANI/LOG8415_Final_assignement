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
    

    #--------------------------------------Create Instances of master and slaves ------------------------------------------------------------

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
    in_,out_,err_=ssh_master.exec_command('sudo apt-get update')
    print('out_:', out_.read())
    print('err_:', err_.read())
    in_,out_,err_=ssh_master.exec_command('sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
    print('out_:', out_.read())
    print('err_:', err_.read())
                                          
    in_,out_,err_=ssh_master.exec_command('sudo bash LOG8415_Final_assignement/Setup/sysbench_initiate_mysql.sh')
    print('out_:', out_.read())
    print('err_:', err_.read())

    # in_,out_,err_=ssh_master.exec_command('sudo bash LOG8415_Final_assignement/Setup/config_mysql_master.sh')
    # print('out_:', out_.read())
    # print('err_:', err_.read())

    print("\n Configuration of mysql on slaves....")
    for i in range (3):
        publicIpAddress_slave=slaves_t2[i][3]
        ssh_slave = paramiko.SSHClient()
        ssh_slave.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_private_slave = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
        ssh_slave.connect(hostname=publicIpAddress_slave,username='ubuntu', pkey=key_private_slave)
        in_,out_,err_=ssh_slave.exec_command('sudo apt-get update && sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
        print('out_:', out_.read())
        print('err_:', err_.read())
        in_,out_,err_=ssh_slave.exec_command('sudo bash LOG8415_Final_assignement/Setup/sysbench_initiate_mysql.sh && sudo bash LOG8415_Final_assignement/Setup/config_mysql_slave.sh ')
        print('out_:', out_.read())
        print('err_:', err_.read())
        in_,out_,err_=ssh_slave.exec_command('sudo apt-get install sysbench -y')
        print('out_:', out_.read())
        print('err_:', err_.read())

    print("\n mysql configs on slaves has been made successfully....")

    in_,out_,err_=ssh_master.exec_command("cd /opt/mysqlcluster/home/mysqlc && sudo scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data && sudo chown -R root /opt/mysqlcluster/home/mysqlc")
    print('out_:', out_.read())
    print('err_:', err_.read())

    in_,out_,err_=ssh_master.exec_command("sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/ && sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &")
    print('out_:', out_.read())
    print('err_:', err_.read())
    

    # ssh_master2 = paramiko.SSHClient()
    # ssh_master2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # key_private_master2 = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    # ssh_master2.connect(hostname=publicIpAddress_master,username='ubuntu', pkey=key_private_master2)
    # in_,out_,err_=ssh_master.exec_command("sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/ && sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &")
    # print('out_:', out_.read())
    # print('err_:', err_.read())
    
    
    time.sleep(50)
    in_,out_,err_=ssh_master.exec_command('sudo bash LOG8415_Final_assignement/Setup/sakila_master.sh')
    print('out_:', out_.read())
    print('err_:', err_.read())

    in_,out_,err_=ssh_master.exec_command('sudo apt-get install sysbench -y')
    print('out_:', out_.read())
    print('err_:', err_.read())


    in_,out_,err_=ssh_master.exec_command('sudo sysbench /usr/share/sysbench/oltp_read_write.lua prepare --db-driver=mysql --mysql-host=ip-172-31-17-142.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password --table-size=50000 ')
    print('out_:', out_.read())
    print('err_:', err_.read())

    in_,out_,err_=ssh_master.exec_command('sudo sysbench /usr/share/sysbench/oltp_read_write.lua run --db-driver=mysql --mysql-host=ip-172-31-17-142.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password --table-size=50000 --threads=8 --time=20 --events=0 >  ')
    print('out_:', out_.read())
    print('err_:', err_.read())

    in_,out_,err_=ssh_master.exec_command('sudo sysbench /usr/share/sysbench/oltp_read_write.lua cleanup --db-driver=mysql --mysql-host=ip-172-31-17-142.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password ')
    print('out_:', out_.read())
    print('err_:', err_.read())

    print("\n mysql config on master has been made successfully....")

    # #--------------------------------------Config mysql on slaves ------------------------------------------------------------
    print("\n Configuration of mysql on slaves....")
    for i in range (3):
        publicIpAddress_slave=slaves_t2[i][3]
        ssh_slave = paramiko.SSHClient()
        ssh_slave.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_private_slave = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
        ssh_slave.connect(hostname=publicIpAddress_slave,username='ubuntu', pkey=key_private_slave)
        in_,out_,err_=ssh_slave.exec_command('sudo apt-get update && sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
        print('out_:', out_.read())
        print('err_:', err_.read())
        in_,out_,err_=ssh_slave.exec_command('sudo bash LOG8415_Final_assignement/Setup/sysbench_initiate_mysql.sh && sudo bash LOG8415_Final_assignement/Setup/config_mysql_slave.sh ')
        print('out_:', out_.read())
        print('err_:', err_.read())
        in_,out_,err_=ssh_slave.exec_command('sudo apt-get install sysbench -y')
        print('out_:', out_.read())
        print('err_:', err_.read())

    print("\n mysql configs on slaves has been made successfully....")
    #--------------------------------------Installing sakila on master  ------------------------------------------------------------
    # print("\n Installation of sakila on master....")

    # ssh_master = paramiko.SSHClient()
    # ssh_master.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # key_private_master = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    # ssh_master.connect(hostname=publicIpAddress_master,username='ubuntu', pkey=key_private_master)
    # ssh_master.exec_command('sudo apt-get update && sudo  mkdir home/sak && cd home/sak')
    # ssh_master.exec_command('sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz && sudo  tar xvf sakila-db.tar.gz')
    # in_,out_,err_=ssh_master.exec_command(' mysql SOURCE /home/sak/sakila-db/sakila-schema.sql &&  mysql SOURCE /home/sak/sakila-db/sakila-data.sql')
    # print('out_:', out_.read())
    # print('err_:', err_.read())

    # print("\n Sakila installation on master has been made successfully....")

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

    