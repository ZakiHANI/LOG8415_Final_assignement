import sys
import boto3
import paramiko
from ..Proxy.SetupANDsend_request_proxy import publicIpAddress_proxy


#Read the proxy mode given in the SSH command
mode = sys.argv[1]
#Reading the request
request = open('/received_request.sql', mode="r", encoding="utf-8").readlines()[0] 

#Create a SSH connection to the proxy using its PublicIpAddress
ssh_proxy = paramiko.SSHClient()
ssh_proxy.set_missing_host_key_policy(paramiko.AutoAddPolicy())
key_private_proxy = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
ssh_proxy.connect(hostname=publicIpAddress_proxy,username='ubuntu', pkey=key_private_proxy)
#Send the request to the trusted_host
in1,out1,err1=ssh_proxy.exec_command('sudo echo ' + "'" + str(request) + "'" + ' >> received_request.sql')

print('-----> Request forwarded to proxy')

commande = f'python3 LOG8415_Final_assignement/Proxy/proxy.py {mode}'
in2,out2,err2=ssh_proxy.exec_command(commande)
print('The output is:',out2.read())
in3,out3,err3=ssh_proxy.exec_command("sudo rm received_request.sql")

