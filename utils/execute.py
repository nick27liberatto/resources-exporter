import shell_commands as cmd
import setup as setup
import paramiko
import os

def ping_data():
    print("ping")
    
def service_data():
    print("service")
    
def port_data():
    print("port")
    
def network_data():
    print("network")
    
def memory_data():
    print("memory")
    
def disk_data():
    print("disk")
    
def cpu_data(user, host):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host,username=user, key_filename=os.path.join(os.path.expanduser('~'), ".ssh", "id_rsa.pub"))
    _stdin, _stdout,_stderr = client.exec_command(cmd.shell_cmd_get_cpu)
    cpu = _stdout.read().decode()
    print(cpu)
    client.close()

def connect_ssh():
    user = "infra"
    #for i in range(len(setup.data()[0])):
        #host = setup.data()[i][0]
    host = "10.41"
    try:
        cpu_data(user, host)
    except:
        pass

connect_ssh()