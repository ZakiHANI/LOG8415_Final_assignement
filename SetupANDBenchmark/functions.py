import configparser
import boto3
import time
import requests
import re 
import json
import fileinput

# This is a function that creates a service resource to establish a connection to ec2: 
def resource_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2_serviceresource =  boto3.resource('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
    
    return(ec2_serviceresource)

# This is a function that creates a service client to establish a connection to ec2: 
def client_ec2(aws_access_key_id, aws_secret_access_key, aws_session_token):
    ec2_serviceclient =  boto3.client('ec2',
                       'us-east-1',
                       aws_access_key_id= aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key ,
                      aws_session_token= aws_session_token) 
   
    
    return(ec2_serviceclient)

# This is a function that creates and checks a keypair resource:  
def create_keypair(key_pair_name, client):
    try:
        keypair = client.create_key_pair(KeyName=key_pair_name)
        print(keypair['KeyMaterial'])
        with open('final_keypair.pem', 'w') as f:
            f.write(keypair['KeyMaterial'])

        return(key_pair_name)

    except:
        print("\n\n============> Warning :  Keypair already created !!!!!!!<==================\n\n")
        return(key_pair_name)

# This is a function that creates a security group:  
def create_security_group(Description,Groupe_name,vpc_id,resource):
    Security_group_ID=resource.create_security_group(
        Description=Description,
        GroupName=Groupe_name,
        VpcId=vpc_id).id
    
    Security_group=resource.SecurityGroup(Security_group_ID)
     
    Security_group.authorize_ingress(
         IpPermissions=[
            {'FromPort':22,
             'ToPort':22,
             'IpProtocol':'tcp',
             'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
            },
            {'FromPort':3306,
             'ToPort':3306,
             'IpProtocol':'tcp',
             'IpRanges':[{'CidrIp':'0.0.0.0/0'}]
            }
            ]
    ) 
    return Security_group_ID

# This is a function that creates a specific security group for the trusted host  
def create_security_group_trusted_host(Description,Groupe_name,vpc_id,resource,allowed_ip_addresses):
    Security_group_ID=resource.create_security_group(
        Description=Description,
        GroupName=Groupe_name,
        VpcId=vpc_id).id
    
    Security_group=resource.SecurityGroup(Security_group_ID)
     
    Security_group.authorize_ingress(
         IpPermissions=[
            {'FromPort':22,
             'ToPort':22,
             'IpProtocol':'tcp',
             'IpRanges':[{'CidrIp':allowed_ip_addresses}]
            }
            ]
    ) 
    return Security_group_ID


#This is a function that creates ec2 instances
#The function returns a list containing the [id of instance,private_dns_name,public_dns_name,public_ip]

def create_instance_ec2(num_instances,ami_id,
    instance_type,key_pair_name,ec2_serviceresource,security_group_id,Availabilityzons,instance_function,user_data):
    instances=[]
    for i in range(num_instances):
        instance=ec2_serviceresource.create_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_pair_name,
            MinCount=1,
            MaxCount=1,
            Placement={'AvailabilityZone':Availabilityzons[i]},
            SecurityGroupIds=[security_group_id] if security_group_id else [],
            UserData=user_data,
            TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'final-'+str(instance_function)+"-"+str(i + 1)
                            },
                        ]
                    },
                ]
        )

        #Wait until the instance is running to get its adresses
        instance[0].wait_until_running()
        instance[0].reload()
        #Get private_dns_name and public_dns_name of the instance and add it in the return
        public_ip = instance[0].public_ip_address
        private_dns_name=instance[0].private_dns_name
        public_dns_name = instance[0].public_dns_name
        instances.append([instance[0].id,private_dns_name,public_dns_name,public_ip])
        print ('Instance: '+str(instance_function)+str(i+1),' having the Id: ',instance[0].id,', the private dns name:',private_dns_name,' and the public dns name: ', public_dns_name, 'is created')
    return instances

#Function to automatically update the ip addresses of msater and slaves in the mysql_config-master.sh file
def ubdate_ip_addresss_master(master_config_file,nmbr_line,new_line):
    try:
        with open(master_config_file, 'r') as f:
            lines = f.readlines()

        if 1 <= nmbr_line <= len(lines):
            del lines[nmbr_line]
            lines[nmbr_line] = new_line
            
            # Write the modified content back to the file
            with open(master_config_file, 'w') as f:
                f.writelines(lines)

    except Exception as e:
        print(f"Error: {str(e)}")

    # # with fileinput.FileInput(master_config_file, inplace=True) as f:
    # #         for i, ligne in enumerate(f, start=1):
    # #             for j in line_numbers:
    # #                 if i == 5:
    # #                 print(nouvelle_valeur)
    # #             else:
    # #                 print(ligne, end='')
    
    # with open(master_config_file,"r") as f:
    #         config_lines=f.readlines()
    # for i in range(len(line_numbers)):
    #     config_lines[line_numbers[i]]=new_lines[i]+'\n'
    #     #config_lines.insert(line_numbers[i],new_lines[i])
    
    # with open(master_config_file, 'w') as f:
    #     f.writelines(config_lines)

