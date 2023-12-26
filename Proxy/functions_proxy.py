import boto3
import paramiko


#Create the function that implement the proxy mode <Direct hit>
def proxy_direct_hit(ssh_master,request):

    #The idea is that we send a write request to the proxy and he will forword it to the master
    in1,out1,err1=ssh_master.exec_command("sudo echo '" + str(request) + "' >> requests.sql" )
    in2,out2,err2=ssh_master.exec_command("sudo /opt/mysqlcluster/home/mysqlc/bin/mysql -h 127.0.0.1 -u root < requests.sql")
    print ('The output is:',out2)
    in3,out3,err3=ssh_master.exec_command("sudo rm requests.sql")


