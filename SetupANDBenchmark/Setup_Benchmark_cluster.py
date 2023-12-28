import configparser
import boto3
from functions import *
import paramiko
import base64
import os

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


    print('============================>The begining of cluster setup')

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
    master_t2= create_instance_ec2(1,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,['us-east-1a'],"master",'')
    print("\n master created successfully with installation of sysbench and mysql")

    print("\n Creating instances : slaves ")
    # Creation of the slaves
    slaves_t2= create_instance_ec2(3,ami_id, instance_type,key_pair_name,ec2_serviceresource,security_group_id,['us-east-1a','us-east-1a','us-east-1a'],"slave",'')
    print("\n slaves created successfully with installation of sysbench and mysql")

    print('============================>The End of cluster setup')

    print('============================>The begining of installation and configuration of mysql clustere')

    #--------------------------------------Update ip addresses of master and slaves in configini.txt and  mysql_slave.sh files ------------------------------------------------------------

    publicIpAddress_master=master_t2[0][3]
    publicIpAddress_slave_1=slaves_t2[0][3]
    publicIpAddress_slave_2=slaves_t2[1][3]
    publicIpAddress_slave_3=slaves_t2[2][3]

    #Update configini.txt
    line2='hostname=ip-'+str(publicIpAddress_master).replace('.','-')+'.ec2.internal'
    line11='hostname=ip-'+str(publicIpAddress_slave_1).replace('.','-')+'.ec2.internal'
    line15='hostname=ip-'+str(publicIpAddress_slave_2).replace('.','-')+'.ec2.internal'
    line19='hostname=ip-'+str(publicIpAddress_slave_3).replace('.','-')+'.ec2.internal'
    ubdate_config_file('configini.txt',2,line2)
    ubdate_config_file('configini.txt',11,line11)
    ubdate_config_file('configini.txt',15,line15)
    ubdate_config_file('configini.txt',19,line19)

    #Update mysql_slave.sh
    line24='sudo /opt/mysqlcluster/home/mysqlc/bin/ndbd -c ec2-'+str(publicIpAddress_master).replace('.','-')+'.compute-1.amazonaws.com:1186'
    ubdate_config_file('mysql_slave.sh',24,line24)

    print("\n Ip addresses of master and slaves are updated successfully in configini.txt and mycnf.txt files....")
    

    #--------------------------------------Config mysql,sakila and sysbench on master ------------------------------------------------------------
    print("\n Configuration of mysql on master....")
    #Create SSH conection to master
    ssh_master = paramiko.SSHClient()
    ssh_master.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_master = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_master.connect(hostname=publicIpAddress_master,username='ubuntu', pkey=key_private_master)

    #Clone my github repoitory
    in1,out1,err1=ssh_master.exec_command('sudo apt-get update && sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
    #Run mysql_master.sh code to configurate mysql on master                                  
    in2,out2,err2=ssh_master.exec_command('sudo bash LOG8415_Final_assignement/SetupANDBenchmark/mysql_master.sh')
    #Run sakila_master.sh code to install sakila
    in3,out3,err3=ssh_master.exec_command('sudo bash LOG8415_Final_assignement/SetupANDBenchmark/sakila_master.sh')
    # Install sysbench for benchmarking
    in4,out4,err4=ssh_master.exec_command('sudo apt-get install sysbench -y')


    #--------------------------------------Config mysql,sakila and sysbench on slaves ------------------------------------------------------------

    print("\n Configuration of mysql on slaves....")
    for i in range (3):
        publicIpAddress_slave=slaves_t2[i][3]
        #Create connection to slave
        ssh_slave = paramiko.SSHClient()
        ssh_slave.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_private_slave = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
        ssh_slave.connect(hostname=publicIpAddress_slave,username='ubuntu', pkey=key_private_slave)
        #Clone my github repository
        in1,out1,err1=ssh_slave.exec_command('sudo apt-get update && sudo git clone https://github.com/ZakiHANI/LOG8415_Final_assignement.git')
        #Run mysql_slave.sh code to configurate mysql on the slave                                  
        in2,out2,err2=ssh_slave.exec_command('sudo bash LOG8415_Final_assignement/SetupANDBenchmark/mysql_slave.sh')
        #Install sysbenh for benchmarking
        in3,out3,err3=ssh_slave.exec_command('sudo apt-get install sysbench -y')

    #--------------------------------------Benchmarking the cluster ------------------------------------------------------------
    
    print('============================>Begining of cluster benchmark')

    #Prepare sysbench benchmark 
    in5,out5,err5=ssh_master.exec_command('sudo sysbench /usr/share/sysbench/oltp_read_write.lua prepare --db-driver=mysql --mysql-host=ip-'+str(publicIpAddress_master).replace('.','-')+'.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password --table-size=40000 --tables=8 ')
    #Run sysbench benchmark
    in6,out6,err6=ssh_master.exec_command('sudo sysbench /usr/share/sysbench/oltp_read_write.lua run --db-driver=mysql --mysql-host=ip-'+str(publicIpAddress_master).replace('.','-')+'.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password --table-size=40000 --tables=8 --threads=11  >  ')
    print('Sysbench output:',out6.read())
    #Cleanup sysbench benchmark
    in7,out7,err7=ssh_master.exec_command('sudo sysbench /usr/share/sysbench/oltp_read_write.lua cleanup --db-driver=mysql --mysql-host=ip-'+str(publicIpAddress_master).replace('.','-')+'.ec2.internal --mysql-db=sakila --mysql-user=root --mysql-password ')
    
    print('============================>End of cluster benchmark')

    

    