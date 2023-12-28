import sys
import boto3
import paramiko


#Read the proxy mode given in the SSH command
mode = sys.argv[1]
#Reading the request
request = open('LOG8415_Final_assignement/received_request.sql', mode="r", encoding="utf-8").readlines()[0] 

publicIpAddress_trusted_host='172.31.10.240'
if 'SELECT *' or ('UPDATE' and 'payment') or ('INSERT' and 'customer') or ('INSERT' and 'payment') in str(request):
    print('access denied')
else :
    print('-----> This is an authorized request')
    #Create a SSH connection to the trusted host using its PublicIpAddress
    ssh_trusted_host = paramiko.SSHClient()
    ssh_trusted_host.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_private_trusted_host = paramiko.RSAKey.from_private_key_file('final_keypair.pem')
    ssh_trusted_host.connect(hostname=publicIpAddress_trusted_host,username='ubuntu', pkey=key_private_trusted_host)
    #Send the request to the trusted_host
    in1,out1,err1=ssh_trusted_host.exec_command('sudo echo ' + "'" + str(request) + "'" + ' >> LOG8415_Final_assignement/received_request.sql')

    print('-----> Request forwarded to trusted host')
    
    commande = f'python3 LOG8415_Final_assignement/Gatekeeper/app_trusted_host.py {mode}'
    in2,out2,err2=ssh_trusted_host.exec_command(commande)
    print(out2.read())
    in3,out3,err3=ssh_trusted_host.exec_command("sudo rm received_request.sql")


