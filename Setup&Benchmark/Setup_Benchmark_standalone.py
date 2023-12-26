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
    

    #--------------------------------------Create Instance of standalone  ------------------------------------------------------------

    # Create standalone t2.micro instance:
    instance_type = "t2.micro"
    
    print("\n Creating instance : standalone ")
    # Creation of the standalone
    standalone_t2= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,['us-east-1a'],"standalone",'')
    print("\n standalone created successfully")

    #--------------------------------------Installing sysbench,mysql and sakila on standalone ------------------------------------------------------------

    #Create an SSH connection to standalone to send commands
    publicIpAddress_standalone=standalone_t2[0][3]
    ssh_standalone = paramiko.SSHClient()
    ssh_standalone.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_standalone = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_standalone.connect(hostname=publicIpAddress_standalone,username='ubuntu', pkey=key_private_standalone)
    
    # in_,out_,err_=ssh_standalone.exec_command('sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git ')
    # print('out_:', out_.read())
    # print('err_:', err_.read())

    # in_,out_,err_=ssh_standalone.exec_command('sudo bash LOG8415_Final_assignement/Setup/sysbench_mysql_sakila_standalone.sh')
    # print('out_:', out_.read())
    # print('err_:', err_.read())


    #Update
    in1,out1,err1=ssh_standalone.exec_command('sudo apt-get update -y')
    #Install mysql server
    in2,out2,err2=ssh_standalone.exec_command('export DEBIAN_FRONTEND=noninteractive && sudo apt-get install mysql-server -y')
    #Install sysbench
    in3,out3,err3=ssh_standalone.exec_command('export DEBIAN_FRONTEND=noninteractive && sudo apt-get install sysbench -y')
    #Get and install sakila
    in4,out4,err4=ssh_standalone.exec_command('sudo wget https://downloads.mysql.com/docs/sakila-db.tar.gz && sudo  tar xvf sakila-db.tar.gz')
    in5,out5,err5=ssh_standalone.exec_command('sudo mysql -u root -e "SOURCE sakila-db/sakila-schema.sql;"')
    in6,out6,err6=ssh_standalone.exec_command('sudo mysql -u root -e "SOURCE sakila-db/sakila-data.sql;"')

    #--------------------------------------Benchmarking of standalone using sysbench ------------------------------------------------------------

    #Creating a user and grant him all privileges on sakila 
    in7,out7,err7=ssh_standalone.exec_command('sudo mysql -e "CREATE USER \'ZAKARIA\'@\'localhost\' IDENTIFIED BY \'FINALPROJECT\';"')
    in8,out8,err8=ssh_standalone.exec_command('sudo mysql -e "GRANT ALL PRIVILEGES ON sakila.* TO \'ZAKARIA\'@\'localhost\';"')
    #Using the user to do sysbench benchmark preparation and run
    in9,out9,err9=ssh_standalone.exec_command('sudo sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=ZAKARIA --mysql_password=FINALPROJECT --table-size=25000 --tables=8 /usr/share/sysbench/oltp_read_write.lua prepare')
    in10,out10,err10=ssh_standalone.exec_command('timr sudo sysbench --db-driver=mysql --mysql-db=sakila --mysql-user=ZAKARIA --mysql_password=FINALPROJECT --table-size=25000 --tables=8 --threads=11 --max-time=20 /usr/share/sysbench/oltp_read_write.lua run')
    