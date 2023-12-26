import configparser
import boto3
import paramiko
import base64
import os
from ..SetupANDBenchmark.functions import *

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
    

#--------------------------------------Create Instance of PROXY  ------------------------------------------------------------

# Create standalone t2.large instance:
instance_type = "t2.large"
    
print("\n Creating instance : Proxy ")
# Creation of the Proxy
Proxy_t2= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,['us-east-1a'],"proxy",'')
print("\n Proxy created successfully")

#--------------------------------------Send requests to Proxy  ------------------------------------------------------------

#Get publicIPAdress of proxy
publicIpAddress_proxy=Proxy_t2[0][3]
#Create SSH connection with proxy
ssh_proxy = paramiko.SSHClient()
ssh_proxy.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key_private_proxy = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
ssh_proxy.connect(hostname=publicIpAddress_proxy,username='ubuntu', pkey=key_private_proxy)
#Clone my github repository
in1,out1,err1=ssh_proxy.exec_command('sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
in2,out2,err2=ssh_proxy.exec_command('sudo bash LOG8415_Final_assignement/Proxy/requirements.sh')
in3,out3,err3=ssh_proxy.exec_command('sudo bash LOG8415_Final_assignement/Proxy/requirements.sh')

while True:
    # Ask user to set the proxy mode to test
    mode = input("Please give me the proxy mode you want to test")

    if mode=='direct_hit':
        #-------> Test a write request
        request_write = input("Plese give me the request you want to send (Write request)")
        #request_write='INSERT INTO sakila.film (title, release_year, rental_rate) VALUES (Oppenheimer,2023,3.7);'
        #load request to the proxy
        in_write,out_write,err_write=ssh_proxy.exec_command('sudo echo ' + "'" + str(request_write) + "'" + ' >> /home/ubuntu/request.sql')
        print('The Output is:', out_write.read())
        #Execute functions_proxy.py code in the proxy with direct_hit mode
        commande_direct_hit = f'python3 LOG8415_Final_assignement/Proxy/functions_proxy.py {mode}'
        in_dir,out_dir,err_dir=ssh_proxy.exec_command(commande_direct_hit)
        print('The Output is:', out_dir.read())
        in_,out_,err_=ssh_proxy.exec_command("sudo rm request.sql")

    if mode=='random':
        #-------> Test a read request
        request_read = input("Plese give me the request you want to send (Read request)")
        #request_read='SELECT first_name, last_name FROM sakila.actor;'
        #load request to the proxy
        in_read,out_read,err_read=ssh_proxy.exec_command('sudo echo ' + "'" + str(request_read) + "'" + ' >> /home/ubuntu/request.sql')
        print('The Output is:', out_read.read())
        #Execute functions_proxy.py code in the proxy with random mode
        commande_random = f'python3 LOG8415_Final_assignement/Proxy/functions_proxy.py {mode}'
        in_random,out_random,err_random=ssh_proxy.exec_command(commande_random)
        print('The Output is:', out_random.read())
        in_,out_,err_=ssh_proxy.exec_command("sudo rm request.sql")


    if mode=='customize':
        #-------> Test a read request
        request_read = input("Plese give me the request you want to send (Read request)")
        #request_read='SELECT first_name, last_name FROM sakila.actor;'
        #load request to the proxy
        in_read,out_read,err_read=ssh_proxy.exec_command('sudo echo ' + "'" + str(request_read) + "'" + ' >> /home/ubuntu/request.sql')
        print('The Output is:', out_read.read())
        #Execute functions_proxy.py code in the proxy with customize mode
        commande_custom = f'python3 LOG8415_Final_assignement/Proxy/functions_proxy.py {mode}'
        in_custom,out_custom,err_custom=ssh_proxy.exec_command(commande_custom)
        print('The Output is:', out_custom.read())
        in_,out_,err_=ssh_proxy.exec_command("sudo rm request.sql")

    # Ask if you keep testing or not
    KeepGoing = input("Do you want to keep the tests ? YES or NO?").upper()

    #If NO , break, if YES continue
    if KeepGoing != 'YES':
        break
