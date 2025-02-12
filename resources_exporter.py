#========================================#
#                Librarys                #
#========================================#

from prometheus_client import start_http_server, Enum, Gauge
import paramiko
import time
import csv
import os

#=======================================#
#               Variables               #
#=======================================#

#Hosts
ip = 0
service_name = 1
machine_name = 2
instances = []
services = []
machines = []

#Ports
ports = []
services_open = []

#Networking
rec = ""
trans = ""
devices = []
received = []
transmitted = []

#Services
enabled_services = []

#================ Regex ================#

#Service
regexService = "%s.*.service.*enabled"
getServiceLen = "systemctl list-unit-files | grep -Po '%s' | wc -l"
findService = "systemctl list-unit-files | grep -Po '%s' | sed -n '%sp' | awk '{print $1}' | tr -d '\n'"
getStatus = "systemctl status %s | grep -Po '(?<=Active:.)\w+' | tr -d '\n'"
getPID = "systemctl status %s | grep -Po '(?<=PID:.)\w+' | tr -d '\n'"

#Ping
getPkg = "ping -c 1 -W 3 %s | grep -Po '(?<=received, )\w' | tr -d '\n'"
getMsec = "ping -c 1 -W 3 %s | grep -Po '(?<=time=)[0-9]+.[0-9]+' | tr -d '\n'"

#Ports
getPortRange = "nmap %s | grep -P '\d+/' | wc -l"
getPortService = "nmap %s | grep -P '\d+/' | awk '{print $3}' | sed -n '%sp' | tr -d '\n'"
getPort = "nmap %s | grep -Po '\d+/' | tr -d '/' | sed -n '%sp' | tr -d '\n'"


#CPU
getCPU = "echo $[100-$(vmstat 1 2|tail -1|awk '{print $15}')] | tr -d '\n'"
getCores = "cat /proc/cpuinfo | grep 'cpu cores' | sed -n 1p | awk '{print $4}'"
        
#Network
rangeDevices = "ip -s link | grep -Po '(?<=\d:\s)\w+' | wc -l"
getDevices = "ip -s link | grep -Po '(?<=\d:\s)\w+' | sed -n '%sp' | tr -d '\n'"
rangeBytes = "ip -s link | awk '{print $1}' | grep -P '\d+$' | wc -l"
getBytes = "ip -s link | awk '{print $1}' | grep -P '\d+$' | sed -n '%sp' | tr -d '\n'" 

#Disk
getDisk = "df | grep -P '/$' | awk '{print $%s}'| tr -d '%%' | tr -d '\n'"

#Memory RAM
getMemPer = "free | grep Mem | awk '{print ($3/$2)*100}' | tr -d '\n'"
getMemSize = "free | grep Mem | awk '{print $2}' | tr -d '\n'"
getMemUsed = "free | grep Mem | awk '{print $3}' | tr -d '\n'"
getMemFree = "free | grep Mem | awk '{print $4}' | tr -d '\n'"

#Memory Swap
getSwapPer = "free | grep Swap | awk '{print ($3/$2)*100}' | tr -d '\n'"
getSwapSize = "free | grep Swap | awk '{print $2}' | tr- d '\n'"
getSwapUsed = "free | grep Swap | awk '{print $3}' | tr -d '\n'"
getSwapFree = "free | grep Swap | awk '{print $4}' | tr -d '\n'"

#=======================================#
#                Metrics                #
#=======================================#

#Ping
service_ping_msec = Gauge('service_ping_msec', 'Ping Milliseconds', ['server_hostname', 'server_ip', 'service_name', 'ping_status'])
service_ping_pkg_loss_percent = Gauge('service_ping_pkg_loss_percent', 'Ping Package Loss in Percentage', ['server_hostname', 'server_ip', 'service_name', 'ping_status'])

#Service
service_current_state = Enum('service_current_state', 'Check if service is running', ['server_hostname', 'server_ip', 'service_name', 'service_pid'], 
                     states=['active', 'inactive', 'enabled', 'disabled', 'static', 'masked', 'alias', 'linked', 'failed', ''])
#Ports
service_ports_open = Gauge('service_ports_open', 'Listening ports for which server', ['server_hostname', 'server_ip', 'service_name', 'listening'])

#CPU
service_cpu_usage_percent = Gauge('service_cpu_usage_percent', 'CPU usage in percentage for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_cpu_cores = Gauge('service_cpu_cores', 'CPU quantity of cores for which Server', ['server_hostname', 'server_ip', 'service_name'])

#Network
service_network_transmitted_bytes = Gauge('service_network_transmitted_bytes', 'Network Transmitted Bytes for which Server', ['server_hostname', 'server_ip', 'service_name', 'interface'])
service_network_received_bytes = Gauge('service_network_received_bytes', 'Network Received Bytes for which Server', ['server_hostname', 'server_ip', 'service_name', 'interface'])

#Disk
service_disk_usage_percent = Gauge('service_disk_usage_percent', 'Disk usage in percentage for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_disk_usage_bytes = Gauge('service_disk_usage_bytes', 'Disk usage in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_disk_size_bytes = Gauge('service_disk_size_bytes', 'Disk size for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_disk_free_bytes = Gauge('service_disk_free_bytes', 'Disk free space in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])

#Memory RAM
service_memory_usage_percent = Gauge('service_memory_usage_percent', 'RAM usage in percentage for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_usage_bytes = Gauge('service_memory_usage_bytes', 'RAM usage in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_size_bytes = Gauge('service_memory_size_bytes', 'RAM size for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_free_bytes = Gauge('service_memory_free_bytes', 'RAM free space in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])

#Memory Swap
service_swap_usage_percent = Gauge('service_swap_usage_percent', 'SWAP usage in percentage for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_usage_bytes = Gauge('service_swap_usage_bytes', 'SWAP usage in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_size_bytes = Gauge('service_swap_size_bytes', 'SWAP size for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_free_bytes = Gauge('service_swap_free_bytes', 'SWAP free space in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])

#=======================================#
#                 Setup                 #
#=======================================#

def setup():
    
    #Get Hosts from CSV File 'host.csv'
    with open('./host/host.csv') as h:
        csv_reader = csv.reader(h)
        for index, row in enumerate(csv_reader):
            instances.append(row[ip])
            services.append(row[service_name])  
            machines.append(row[machine_name])          

    #Get List Length
    lenList = len(services)
    fetch_data(lenList)

#============================================#
#                 Fetch Data                 #
#============================================#

def fetch_data(lenList):

    #Iterate through instances
    for i in range(lenList):
        
        #Identification
        name = services[i]
        machine = machines[i]
        
        #Auth
        host = instances[i]
        username = "infra"

        #SSH Connection
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, key_filename=os.path.join(os.path.expanduser('~'), ".ssh", "id_rsa.pub"))

        #=========================================#
        #                  Ping                   #
        #=========================================#   
        
        #Get Package Loss Percentage
        pkg = os.popen(getPkg%host).read()
        #Get Ping Milliseconds
        msec = os.popen(getMsec%host).read()
        
        #Format to int/float
        if pkg == "":
            pkg = 0
        else:
            pkg = int(pkg)
        
        if msec == "":
            msec = 0.0
        else:
            msec = float(msec)
        
        #Define Status Based on Package Loss
        if pkg == 100:
            status = "inactive"
        elif pkg == 0:
            status = "active"
        else:
            status = "deprecated"
        
        #============== Export Metrics ==============#
        
        service_ping_pkg_loss_percent.labels(f'{machine}', f'{host}', f'{name}', f'{status}').set(pkg)
        service_ping_msec.labels(f'{machine}', f'{host}', f'{name}', f'{status}').set(msec)
 
        #=========================================#
        #                 Service                 #
        #=========================================#   
            
        #Get Services Length
        _stdin, _stdout,_stderr = client.exec_command(getServiceLen%(regexService%(name)))
        serviceLen = _stdout.read().decode()
        
        #Get Service Name
        for srv_index in range(int(serviceLen)):
            srv = srv_index + 1
            _stdin, _stdout,_stderr = client.exec_command(findService%(regexService%(name), srv))
            service = _stdout.read().decode()
            
            #Get Status
            _stdin, _stdout,_stderr = client.exec_command(getStatus%(service))
            status = _stdout.read().decode()
            
            #Get Process Identification
            _stdin, _stdout,_stderr = client.exec_command(getPID%(service))
            pid = _stdout.read().decode()

        #============== Export Metrics ==============#
        
            service_current_state.labels(f'{machine}', f'{host}', f'{name}', f'{pid}').state(status)  
        
        #=========================================#
        #                  Ports                  #
        #=========================================#   
        
        #Get rows length
        portRange = os.popen(getPortRange%(host)).read()
        
        #Get Ports/Service Line by Line
        for r in range(int(portRange)):
            row = r + 1
            
            #Get Port Numeric
            port = os.popen(getPort%(host, row)).read()
            
            #Get Service Listening on Port
            openService = os.popen(getPortService%(host, row)).read()

        #============== Export Metrics ==============#
        
            #Validates if the arrays are in the same length
            if (len(ports)) == (len(services_open)):
                #Combines/Zip ports and open listening services for fast searching and synchronism
                for p, s in zip(port, openService):
                    #Search if the value is already in the array
                    search_p = p in ports
                    search_s = s in services_open
                    #If the value already is in the array, don't add (skip)
                    if (search_p) or (search_s):
                        print("invalid")
                    #Else append to array
                    else:
                        ports.append(port)
                        services_open.append(openService)
            #If they are not in the same length, skip and output
            else:
                print(ports, services_open)
        
        #Add metric in the range of ports length
        for add_metric in range(len(ports)):
            service_ports_open.labels(f'{machine}', f'{host}', f'{name}', f'{services_open[add_metric]}').set(ports[add_metric])
        
        #Clear Arrays for which filling
        ports.clear()
        services_open.clear()
        
        #=========================================#
        #                   CPU                   #
        #=========================================# 
        
        #Get CPU Usage in %
        _stdin, _stdout,_stderr = client.exec_command(getCPU)
        cpu = _stdout.read().decode()
        
        #Get CPU Cores
        _stdin, _stdout,_stderr = client.exec_command(getCores)
        cores = _stdout.read().decode()       
        
        #============== Export Metrics ==============#
        
        service_cpu_usage_percent.labels(f'{machine}', f'{host}', f'{name}').set(cpu)
        service_cpu_cores.labels(f'{machine}', f'{host}', f'{name}').set(cores)

        #===========================================#
        #                  Network                  #
        #===========================================# 

        #Get rows length of Network Interfaces/Devices
        _stdin, _stdout,_stderr = client.exec_command(rangeDevices)
        rangeDev = _stdout.read().decode()
        
        #Get rows length of RX/TX Bytes
        _stdin, _stdout,_stderr = client.exec_command(rangeBytes)
        rangeBy = _stdout.read().decode()
        
        #Get Devices based on the rows length
        for d in range(int(rangeDev)):
            row = d + 1
            _stdin, _stdout,_stderr = client.exec_command(getDevices%row)
            device = _stdout.read().decode()
            devices.append(device)

        #Get RX/TX Bytes based on the rows length
        for b in range(int(rangeBy)):
            row = b + 1
            #If row index is even, append TX
            if row % 2 == 0:
                _stdin, _stdout,_stderr = client.exec_command(getBytes%row)
                trans = _stdout.read().decode()
                if trans != "":
                    transmitted.append(trans)
            #If row index is odd, append RX 
            else:
                _stdin, _stdout,_stderr = client.exec_command(getBytes%row)
                rec = _stdout.read().decode()
                if rec != "":
                    received.append(rec)

        #============== Export Metrics ==============#
        
        for l in range(len(devices)):
            service_network_transmitted_bytes.labels(f'{machine}', f'{host}', f'{name}', f'{devices[l]}').set(transmitted[l])
            service_network_received_bytes.labels(f'{machine}', f'{host}', f'{name}', f'{devices[l]}').set(received[l])
        
        #Empty array for new append
        devices.clear()
        received.clear()
        transmitted.clear()

        #===========================================#
        #                   Disk                    #
        #===========================================# 

        #Get Disk Size
        _stdin, _stdout,_stderr = client.exec_command(getDisk%2)
        diskSize = _stdout.read().decode()

        #Get Disk Used
        _stdin, _stdout,_stderr = client.exec_command(getDisk%3)
        diskUsed = _stdout.read().decode()
        
        #Get Disk Free Space
        _stdin, _stdout,_stderr = client.exec_command(getDisk%4)
        diskFree = _stdout.read().decode()
        
        #Get Disk Usage Percentage
        _stdin, _stdout,_stderr = client.exec_command(getDisk%5)
        diskPer = _stdout.read().decode()

        #============== Export Metrics ==============#

        service_disk_usage_percent.labels(f'{machine}', f'{host}', f'{name}').set(diskPer)
        service_disk_usage_bytes.labels(f'{machine}', f'{host}', f'{name}').set(diskUsed)
        service_disk_size_bytes.labels(f'{machine}', f'{host}', f'{name}').set(diskSize)
        service_disk_free_bytes.labels(f'{machine}', f'{host}', f'{name}').set(diskFree)

        #=========================================#
        #                   CPU                   #
        #=========================================# 
         
        #Get Mem Use in percentage
        _stdin, _stdout,_stderr = client.exec_command(getMemPer)
        memPer = _stdout.read().decode()

        #Get Mem size
        _stdin, _stdout,_stderr = client.exec_command(getMemSize)
        memSize = _stdout.read().decode()
        
        #Get Mem Usage in bytes
        _stdin, _stdout,_stderr = client.exec_command(getMemUsed)
        memUsed = _stdout.read().decode()

        #Get Mem free space in bytes
        _stdin, _stdout,_stderr = client.exec_command(getMemFree)
        memFree = _stdout.read().decode()
                
        #Get Swap Use in percentage
        _stdin, _stdout,_stderr = client.exec_command(getSwapPer)
        swapPer = _stdout.read().decode()

        #Get Swap size
        _stdin, _stdout,_stderr = client.exec_command(getSwapSize)
        swapSize = _stdout.read().decode()
        
        #Get Swap Usage in bytes
        _stdin, _stdout,_stderr = client.exec_command(getSwapUsed)
        swapUsed = _stdout.read().decode()

        #Get Swap free space in bytes
        _stdin, _stdout,_stderr = client.exec_command(getSwapFree)
        swapFree = _stdout.read().decode()
        
        #Rounding the Percentage
        if swapSize == "":
            swapSize = 0
            swapPer = 0
        else:
            swapPer = (round(float(swapPer)))
        memPer = (round(float(memPer)))
        
        #============== Export Metrics ==============#
        
        #Memory RAM
        service_memory_usage_percent.labels(f'{machine}', f'{host}', f'{name}').set(memPer)
        service_memory_usage_bytes.labels(f'{machine}', f'{host}', f'{name}').set(memUsed)
        service_memory_size_bytes.labels(f'{machine}', f'{host}', f'{name}').set(memSize)
        service_memory_free_bytes.labels(f'{machine}', f'{host}', f'{name}').set(memFree)

        #Memory Swap
        service_swap_usage_percent.labels(f'{machine}', f'{host}', f'{name}').set(swapPer)
        service_swap_usage_bytes.labels(f'{machine}', f'{host}', f'{name}').set(swapUsed)
        service_swap_size_bytes.labels(f'{machine}', f'{host}', f'{name}').set(swapSize)
        service_swap_free_bytes.labels(f'{machine}', f'{host}', f'{name}').set(swapFree)
        
        #========== Close Connection ==========#
        client.close()
                
#==============================================#
#                 Start Server                 #
#==============================================#

if __name__ == '__main__':
    start_http_server(9095)
    print("Exporter running at http://localhost:9095")

    while True:
        setup()
        time.sleep(5)
