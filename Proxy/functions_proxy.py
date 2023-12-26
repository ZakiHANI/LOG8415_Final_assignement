import boto3
import paramiko
import random


#Create the function that implement the proxy mode <Direct hit>
#The idea is that we send a write request to the proxy and it will forword it to the master

def proxy_direct_hit(publicIpAddress_master,request):
    'The function takes as arguments the publicIpAddress_master and the sent request'
        
    #Create a SSH connection to the master using its chosen PublicIpAddress
    ssh_master = paramiko.SSHClient()
    ssh_master.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_master = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_master.connect(hostname=publicIpAddress_master,username='ubuntu', pkey=key_private_master)
    #Send the request to the master
    in1,out1,err1=ssh_master.exec_command("sudo echo '" + str(request) + "' >> requests.sql" )
    in2,out2,err2=ssh_master.exec_command("sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -h 127.0.0.1 -u root < requests.sql")
    #Print the Output
    print ('The output is:',out2)
    #Remove requests.sql
    in3,out3,err3=ssh_master.exec_command("sudo rm requests.sql")


#Create the function that implement the proxy mode <Random>
#The idea is that we send a read request to the proxy and it will forword it to a random slave

def proxy_random(publicIpAddress_slaves_list,request,publicIpAddress_master):
    'The function takes as arguments the list of publicIpAddress_slaves, the sent request and the publicIpAddress of the master'

    #Choice of a randme publicIpaddresse from publicIpaddresses of slaves
    PublicIpAddress_chosen=random.choice(publicIpAddress_slaves_list)
    print('The randomly chosen slave has the IP Address :',PublicIpAddress_chosen)
    #Create a SSH connection to the chosen slave using its chosen PublicIpAddress
    ssh_slave = paramiko.SSHClient()
    ssh_slave.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_slave = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_slave.connect(hostname=PublicIpAddress_chosen,username='ubuntu', pkey=key_private_slave)
    #Send the request to the chosen slave
    in1,out1,err1=ssh_slave.exec_command("sudo echo '" + str(request) + "' >> requests.sql" )
    in2,out2,err2=ssh_slave.exec_command("sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -h "+str(publicIpAddress_master).replace('.','-')+".compute-1.amazonaws.com -u ZAKARIA < requests.sql")
    #Print the Output
    print ('The output is:',out2)
    #Remove requests.sql
    in3,out3,err3=ssh_slave.exec_command("sudo rm requests.sql")

