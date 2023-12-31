import configparser
import boto3
import paramiko
import base64
import os
from ..SetupANDBenchmark.functions import *
from ..Proxy.SetupANDsend_request_proxy import publicIpAddress_proxy

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


print('============================>The begining of Gatekeeper and trusted host setup')

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


#--------------------------------------Create a security group for gatekeepr --------------------------------
security_group_getkeeper_id = create_security_group("sec_group","final_security_group",vpc_id,ec2_serviceresource)  
security_group_trusted_host_id = create_security_group("sec_group","trusted_host_security_group",vpc_id,ec2_serviceresource,allowed_ip_addresses)  

#--------------------------------------Create Instance of Gatekeeper ------------------------------------------------------------

# Create standalone t2.large instance:
instance_type = "t2.large"
    
print("\n Creating instance : Gatekeeper ")
# Creation of the Gatkeeper
Gatekeeper_t2= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_getkeeper_id,['us-east-1a'],"Gatekeeper",'')
print("\n Gatekeeper created successfully")

#--------------------------------------Create a specific security group for trusted host --------------------------------
#Get publicIPAdress of Gatekeeper
publicIpAddress_gatekeeper=Gatekeeper_t2[0][3]
#Set allowed ip_addresses to communicate with trusted host (just proxy and gatekeeper)
allowed_ip_addresses=[publicIpAddress_proxy,publicIpAddress_gatekeeper]

#--------------------------------------Create Instance of Gatekeeper ------------------------------------------------------------
print("\n Creating instance : Trusted host ")
# Creation of the Trusted host

Trusted_host_t2= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_trusted_host_id,['us-east-1a'],"Trusted_host",'')
print("\n Trusted host created successfully")

print('============================>The end of Gatekeeper and trusted host setup')

#--------------------------------------Send requests to Gatekeeper  ------------------------------------------------------------


#Create SSH connection with Gatekeeper
ssh_gatekeeper = paramiko.SSHClient()
ssh_gatekeeper.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key_private_gatekeeper = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
ssh_gatekeeper.connect(hostname=publicIpAddress_gatekeeper,username='ubuntu', pkey=key_private_gatekeeper)
#Clone my github repository
in1,out1,err1=ssh_gatekeeper.exec_command('sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
in2,out2,err2=ssh_gatekeeper.exec_command('sudo bash LOG8415_Final_assignement/Gatekeeper/requirements.sh')

#Get publicIPAdress of Trusted host
publicIpAddress_trusted_host=Trusted_host_t2[0][3]
#Create SSH connection with Trusted host
ssh_trusted_host = paramiko.SSHClient()
ssh_trusted_host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key_private_trusted_host = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
ssh_trusted_host.connect(hostname=publicIpAddress_trusted_host,username='ubuntu', pkey=key_private_trusted_host)
#Clone my github repository
in1,out1,err1=ssh_trusted_host.exec_command('sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
in2,out2,err2=ssh_trusted_host.exec_command('sudo bash LOG8415_Final_assignement/Gatekeeper/requirements.sh')

while True:
    # Ask user to set the request to send 
    request = input("Please give me your request")
    mode = input("Please give me the proxy mode")
    in1,out1,err1=ssh_gatekeeper.exec_command('sudo echo ' + "'" + str(request) + "'" + ' >> received_request.sql')
    print('The Output is:', out1.read())
    commande = f'python3 LOG8415_Final_assignement/Gatekeeper/app_gatekeeper.py {mode}'
    in2,out2,err2=ssh_gatekeeper.exec_command(commande)
    print('The Output is:', out2.read())
    in_,out_,err_=ssh_gatekeeper.exec_command("sudo rm received_request.sql")

    # Ask if you keep testing or not
    KeepGoing = input("Do you want to keep the tests ? YES or NO?").upper()

    #If NO , break, if YES continue
    if KeepGoing != 'YES':
        break
