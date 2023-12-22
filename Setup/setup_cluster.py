import configparser
import boto3
from functions import *
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


    #--------------------------------------Config mysql on master and slaves ------------------------------------------------------------

    #--------------------------------------Installing sakila on master and slaves ------------------------------------------------------------


    print('============================>SETUP ends')