import sys
import boto3
import paramiko
import random
import time
from ping3 import ping

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
    print ('The output is:',out2.read())
    #Remove requests.sql
    in3,out3,err3=ssh_master.exec_command("sudo rm requests.sql")


#Create the function that implement the proxy mode <Random>
#The idea is that we send a read request to the proxy and it will forword it to a random slave

def proxy_random(dict_slaves_publicIpAddress,request,publicIpAddress_master):
    'The function takes as arguments a dictianry (keys=slaves names and values=slaves publicIpAddresses),' 
    'the sent request and the publicIpAddress of the master'

    #Choice of a randome slave from list of slaves (dictionary keys)
    chosen_slave=random.choice(dict_slaves_publicIpAddress.keys())
    print('The randomly chosen slave is :',chosen_slave)
    PublicIpAddress_chosen=dict_slaves_publicIpAddress[chosen_slave]
    #Create a SSH connection to the chosen slave using its chosen PublicIpAddress
    ssh_slave = paramiko.SSHClient()
    ssh_slave.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_slave = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_slave.connect(hostname=PublicIpAddress_chosen,username='ubuntu', pkey=key_private_slave)
    #Send the request to the chosen slave
    in1,out1,err1=ssh_slave.exec_command("sudo echo '" + str(request) + "' >> requests.sql" )
    in2,out2,err2=ssh_slave.exec_command("sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -h ec2-"+str(publicIpAddress_master).replace('.','-')+".compute-1.amazonaws.com -u ZAKARIA < requests.sql")
    #Print the Output
    print ('The output is:',out2.read())
    #Remove requests.sql
    in3,out3,err3=ssh_slave.exec_command("sudo rm requests.sql")

#Create the function that implement the proxy mode <Customize>
#The idea is that we send a read request to the proxy and it will ping all the nodes and measure the ping time of each one ,
#and then and send the request to the node with mimimum response time.
def proxy_customize(dict_nodes_publicIpAddress,request,publicIpAddress_master):
    'The function takes as arguments a dictianry (keys=nodes names and values=nodes publicIpAddresses) ,' 
    'the sent request and the publicIpAddress of the master'

    ping_times={node: ping('ec2-'+str(dict_nodes_publicIpAddress[node]).replace('.','-')+".compute-1.amazonaws.com") for node in dict_nodes_publicIpAddress.keys()}
    Best_node=min(ping_times, key=ping_times.get)
    print('The server with minimum ping is :',Best_node)
    #Create a SSH connection to the selected node using its PublicIpAddress
    ssh_selected_node = paramiko.SSHClient()
    ssh_selected_node.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_selected_node = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_selected_node.connect(hostname=dict_nodes_publicIpAddress[Best_node],username='ubuntu', pkey=key_private_selected_node)
    #Send the request to the selected node 
    in1,out1,err1=ssh_selected_node.exec_command("sudo echo '" + str(request) + "' >> requests.sql" )
    in2,out2,err2=ssh_selected_node.exec_command("sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -h ec2-"+str(publicIpAddress_master).replace('.','-')+".compute-1.amazonaws.com -u ZAKARIA < requests.sql")
    #Print the Output
    print ('The output is:',out2.read())
    #Remove requests.sql
    in3,out3,err3=ssh_selected_node.exec_command("sudo rm requests.sql")

#Read the proxy mode given in the SSH command
mode = sys.argv[1]
#Reading the request
request = open('/home/ubuntu/request.sql', mode="r", encoding="utf-8").readlines()[0]  

publicIpAddress_master='172.31.24.243'
dict_slaves_publicIpAddress={'slave-1':'172.31.30.207','slave-2':'172.31.23.68','slave-3':'172.31.24.170'}
dict_nodes_publicIpAddress={'master':'172.31.24.243','slave-1':'172.31.30.207','slave-2':'172.31.23.68','slave-3':'172.31.24.170'}

#execute the function of direct hit if we want to test the direct hit mode
if mode=='direct hit':
    proxy_direct_hit(publicIpAddress_master,request)

#execute the function of random if we want to test the random mode
if mode=='random':
    proxy_random(dict_slaves_publicIpAddress,request,publicIpAddress_master)

#execute the function of customize if we want to test the customize mode
if mode=='customize':
    proxy_customize(dict_nodes_publicIpAddress,request,publicIpAddress_master)
