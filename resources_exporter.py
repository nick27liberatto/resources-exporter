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

#Host Configuration
IP = 0
SERVICE = 1
HOSTNAME = 2
vm_ips = []
vm_services = []
vm_hostnames = []

#Ports
ports = []
ports_services = []

#Networking
received_bytes = ""
transmitted_bytes = ""
network_devices = []
network_device_received_bytes = []
network_device_transmitted_bytes = []

#================ Regex ================#

#Optional Connection Configuration
get_local_user = "echo $USER | tr -d '\n'"

#Service
regex_service_name = "%s.*.service.*enabled"
regex_service_qnt = "systemctl list-unit-files | grep -Po '%s' | wc -l"
regex_get_service = "systemctl list-unit-files | grep -Po '%s' | sed -n '%sp' | awk '{print $1}' | tr -d '\n'"
regex_get_status = "systemctl status %s | grep -Po '(?<=Active:.)\w+' | tr -d '\n'"
regex_get_pid = "systemctl status %s | grep -Po '(?<=PID:.)\w+' | tr -d '\n'"

#Ping
regex_get_pkg = "ping -c 1 -W 3 %s | grep -Po '(?<=received, )\w' | tr -d '\n'"
regex_get_msec = "ping -c 1 -W 3 %s | grep -Po '(?<=time=)[0-9]+.[0-9]+' | tr -d '\n'"

#Ports
regex_ports_qnt = "nmap %s | grep -P '\d+/' | wc -l"
regex_get_ports_services = "nmap %s | grep -P '\d+/' | awk '{print $3}' | sed -n '%sp' | tr -d '\n'"
regex_get_ports = "nmap %s | grep -Po '\d+/' | tr -d '/' | sed -n '%sp' | tr -d '\n'"


#CPU
regex_get_cpu = "echo $[100-$(vmstat 1 2|tail -1|awk '{print $15}')] | tr -d '\n'"
regex_get_cores = "cat /proc/cpuinfo | grep 'cpu cores' | sed -n 1p | awk '{print $4}'"
        
#Network
regex_devices_qnt = "ip -s link | grep -Po '(?<=\d:\s)\w+' | wc -l"
regex_get_devices = "ip -s link | grep -Po '(?<=\d:\s)\w+' | sed -n '%sp' | tr -d '\n'"
regex_tx_rx_qnt = "ip -s link | awk '{print $1}' | grep -P '\d+$' | wc -l"
regex_get_tx_rx_bytes = "ip -s link | awk '{print $1}' | grep -P '\d+$' | sed -n '%sp' | tr -d '\n'" 

#Disk '/' for Other Resources
regex_get_disk = "df | grep -P '/$' | awk '{print $%s}' | tr -d '%%' | tr -d '\n'"

#Disk '/opensearch' for OpenSearch
regex_get_disk_opensearch = "df | grep opensearch | awk '{print $%s}' | tr -d '%%' | tr -d '\n'"

#DIsk '/data/backup' for MongoDB
regex_get_disk_mongodb = "df | grep mongodb | awk '{print $%s}' | tr -d '%%' | tr -d '\n'"

#Memory RAM
regex_get_mem_usage_percent = "free | grep Mem | awk '{print ($3/$2)*100}' | tr -d '\n'"
regex_get_mem_total_bytes = "free | grep Mem | awk '{print $2}' | tr -d '\n'"
regex_get_mem_used_bytes = "free | grep Mem | awk '{print $3}' | tr -d '\n'"
regex_get_mem_free_bytes = "free | grep Mem | awk '{print $4}' | tr -d '\n'"

#Memory Swap
regex_get_swp_usage_percent = "free | grep Swap | awk '{print ($3/$2)*100}' | tr -d '\n'"
regex_get_swp_total_bytes = "free | grep Swap | awk '{print $2}' | tr- d '\n'"
regex_get_swp_used_bytes = "free | grep Swap | awk '{print $3}' | tr -d '\n'"
regex_get_swp_free_bytes = "free | grep Swap | awk '{print $4}' | tr -d '\n'"

#=======================================#
#                Metrics                #
#=======================================#

#Ping
service_ping_msec = Gauge('service_ping_msec', 'Ping Milliseconds', ['server_hostname', 'server_ip', 'service_name', 'ping_status'])
service_ping_pkg_loss_percent = Gauge('service_ping_pkg_loss_percent', 'Ping Package Loss in Percentage', ['server_hostname', 'server_ip', 'service_name', 'ping_status'])

#Service
service_state = Enum('service_state', 'Check if service is running', ['server_hostname', 'server_ip', 'service_scope', 'service_name', 'service_pid'], 
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
service_disk_total_bytes = Gauge('service_disk_total_bytes', 'Disk size for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_disk_free_bytes = Gauge('service_disk_free_bytes', 'Disk free space in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])

#Memory RAM
service_memory_usage_percent = Gauge('service_memory_usage_percent', 'RAM usage in percentage for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_usage_bytes = Gauge('service_memory_usage_bytes', 'RAM usage in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_total_bytes = Gauge('service_memory_total_bytes', 'RAM size for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_free_bytes = Gauge('service_memory_free_bytes', 'RAM free space in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])

#Memory Swap
service_swap_usage_percent = Gauge('service_swap_usage_percent', 'SWAP usage in percentage for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_usage_bytes = Gauge('service_swap_usage_bytes', 'SWAP usage in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_total_bytes = Gauge('service_swap_total_bytes', 'SWAP size for which Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_free_bytes = Gauge('service_swap_free_bytes', 'SWAP free space in bytes for which Server', ['server_hostname', 'server_ip', 'service_name'])

#=======================================#
#                 Setup                 #
#=======================================#

def setup():
    
    #Get Hosts from CSV File 'host.csv'
    with open('./host/host.csv') as h:
        csv_reader = csv.reader(h)
        for index, row in enumerate(csv_reader):
            vm_ips.append(row[IP])
            vm_services.append(row[SERVICE])  
            vm_hostnames.append(row[HOSTNAME])          

    #Get List Length
    vm_services_qnt = len(vm_services)
    fetch_data(vm_services_qnt)

#============================================#
#                 Fetch Data                 #
#============================================#

def fetch_data(vm_services_qnt):

    #Iterate through instances
    for i in range(vm_services_qnt):
        
        #Identification
        service_scope = vm_services[i]
        hostname = vm_hostnames[i]
        
        #Authentication
        host = vm_ips[i]
        username = "infra" # optional: os.popen(get_local_user).read()

        #================ SSH Connection ================#
        
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, username=username, key_filename=os.path.join(os.path.expanduser('~'), ".ssh", "id_rsa.pub"))

        #=========================================#
        #                  Ping                   #
        #=========================================#   
        
        #Get Package Loss Percentage
        pkg = os.popen(regex_get_pkg%host).read()
        #Get Ping Milliseconds
        msec = os.popen(regex_get_msec%host).read()
        
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
            status = "timeout"
        elif pkg == 0:
            status = "stable"
        else:
            status = "unstable"
        
        #============== Export Metrics ==============#
        
        service_ping_pkg_loss_percent.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{status}').set(pkg)
        service_ping_msec.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{status}').set(msec)
 
        #=========================================#
        #                 Service                 #
        #=========================================#   
            
        #Get Services Length
        _stdin, _stdout,_stderr = client.exec_command(regex_service_qnt%(regex_service_name%(service_scope)))
        services_qnt = _stdout.read().decode()
        
        #Iterate through services in the current scope (Ex: Opensearch has more than one service running.)
        for service_counter in range(int(services_qnt)):
            counter = service_counter + 1
            
            #Get Service Name
            _stdin, _stdout,_stderr = client.exec_command(regex_get_service%(regex_service_name%(service_scope), counter))
            service = _stdout.read().decode()
            
            #Get Status
            _stdin, _stdout,_stderr = client.exec_command(regex_get_status%(service))
            status = _stdout.read().decode()
            
            #Get Process Identification
            _stdin, _stdout,_stderr = client.exec_command(regex_get_pid%(service))
            pid = _stdout.read().decode()

        #============== Export Metrics ==============#
        
            service_state.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{service}', f'{pid}').state(status)  
        
        #=========================================#
        #                  Ports                  #
        #=========================================#   
        
        #Get rows length
        portRange = os.popen(regex_ports_qnt%(host)).read()
        
        #Get Ports/Service Line by Line
        for r in range(int(portRange)):
            row = r + 1
            
            #Get Port Numeric
            port = os.popen(regex_get_ports%(host, row)).read()
            
            #Get Service Listening on Port
            port_service = os.popen(regex_get_ports_services%(host, row)).read()

        #============== Export Metrics ==============#
        
            #Validates if the arrays are in the same length
            if (len(ports)) == (len(ports_services)):
                
                #Combines/Zip ports and open listening services for fast searching and synchronism
                for p, s in zip(port, port_service):
                    
                    #Search if the value is already in the array
                    search_port = p in ports
                    search_port_service = s in ports_services
                    
                    #If the value already is in the array, don't add (skip)
                    if (search_port) or (search_port_service):
                        print("Port or Service already in list")
                    
                    #Else append to array
                    else:
                        ports.append(port)
                        ports_services.append(port_service)
            
            #If they are not in the same length, skip and output
            else:
                print(ports, ports_services)
        
        #Add metric in the range of ports length
        for counter in range(len(ports)):
            service_ports_open.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{ports_services[counter]}').set(ports[counter])
        
        #Clear Arrays for which filling
        ports.clear()
        ports_services.clear()
        
        #=========================================#
        #                   CPU                   #
        #=========================================# 
        
        #Get CPU Usage in %
        _stdin, _stdout,_stderr = client.exec_command(regex_get_cpu)
        cpu = _stdout.read().decode()
        
        #Get CPU Cores
        _stdin, _stdout,_stderr = client.exec_command(regex_get_cores)
        cores = _stdout.read().decode()       
        
        #============== Export Metrics ==============#
        
        service_cpu_usage_percent.labels(f'{hostname}', f'{host}', f'{service_scope}').set(cpu)
        service_cpu_cores.labels(f'{hostname}', f'{host}', f'{service_scope}').set(cores)

        #===========================================#
        #                  Network                  #
        #===========================================# 

        #Get rows length of Network Interfaces/Devices
        _stdin, _stdout,_stderr = client.exec_command(regex_devices_qnt)
        devices_qnt = _stdout.read().decode()
        
        #Get rows length of RX/TX Bytes
        _stdin, _stdout,_stderr = client.exec_command(regex_tx_rx_qnt)
        tx_rx_qnt = _stdout.read().decode()
        
        #Get Devices based on the rows length
        for counter_device in range(int(devices_qnt)):
            counter = counter_device + 1
            _stdin, _stdout,_stderr = client.exec_command(regex_get_devices%counter)
            device = _stdout.read().decode()
            network_devices.append(device)

        #Get RX/TX Bytes based on the rows length
        for counter_rx_tx in range(int(tx_rx_qnt)):
            counter = counter_rx_tx + 1
            
            #If row index is even, append TX
            if counter % 2 == 0:
                _stdin, _stdout,_stderr = client.exec_command(regex_get_tx_rx_bytes%counter)
                transmitted_bytes = _stdout.read().decode()
                if transmitted_bytes != "":
                    network_device_transmitted_bytes.append(transmitted_bytes)
            
            #If row index is odd, append RX 
            else:
                _stdin, _stdout,_stderr = client.exec_command(regex_get_tx_rx_bytes%counter)
                received_bytes = _stdout.read().decode()
                if received_bytes != "":
                    network_device_received_bytes.append(received_bytes)

        #============== Export Metrics ==============#
        
        for counter in range(len(network_devices)):
            service_network_transmitted_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{network_devices[counter]}').set(network_device_transmitted_bytes[counter])
            service_network_received_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{network_devices[counter]}').set(network_device_received_bytes[counter])
        
        #Empty array for new append
        network_devices.clear()
        network_device_transmitted_bytes.clear()
        network_device_received_bytes.clear()

        #===========================================#
        #                   Disk                    #
        #===========================================# 

        if "qa-opensearch_data" in hostname:
            disk = regex_get_disk_opensearch
        elif "mongo" in hostname:
            disk = regex_get_disk_mongodb
        else:
            disk = regex_get_disk
        
        #Get Disk Size
        _stdin, _stdout,_stderr = client.exec_command(disk%2)
        disk_total_bytes = _stdout.read().decode()

        #Get Disk Used
        _stdin, _stdout,_stderr = client.exec_command(disk%3)
        disk_used_bytes = _stdout.read().decode()
        
        #Get Disk Free Space
        _stdin, _stdout,_stderr = client.exec_command(disk%4)
        disk_free_bytes = _stdout.read().decode()
        
        #Get Disk Usage Percentage
        _stdin, _stdout,_stderr = client.exec_command(disk%5)
        disk_percent = _stdout.read().decode()

        #============== Export Metrics ==============#
        
        
        service_disk_usage_percent.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_percent)
        service_disk_usage_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_used_bytes)
        service_disk_total_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_total_bytes)
        service_disk_free_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_free_bytes)

        #=========================================#
        #                   CPU                   #
        #=========================================# 
         
        #Get Mem Use in percentage
        _stdin, _stdout,_stderr = client.exec_command(regex_get_mem_usage_percent)
        mem_percent = _stdout.read().decode()

        #Get Mem size
        _stdin, _stdout,_stderr = client.exec_command(regex_get_mem_total_bytes)
        mem_total_bytes = _stdout.read().decode()
        
        #Get Mem Usage in bytes
        _stdin, _stdout,_stderr = client.exec_command(regex_get_mem_used_bytes)
        mem_used_bytes = _stdout.read().decode()

        #Get Mem free space in bytes
        _stdin, _stdout,_stderr = client.exec_command(regex_get_mem_free_bytes)
        mem_free_bytes = _stdout.read().decode()
                
        #Get Swap Use in percentage
        _stdin, _stdout,_stderr = client.exec_command(regex_get_swp_usage_percent)
        swap_percent = _stdout.read().decode()

        #Get Swap size
        _stdin, _stdout,_stderr = client.exec_command(regex_get_swp_total_bytes)
        swap_total_bytes = _stdout.read().decode()
        
        #Get Swap Usage in bytes
        _stdin, _stdout,_stderr = client.exec_command(regex_get_swp_used_bytes)
        swap_used_bytes = _stdout.read().decode()

        #Get Swap free space in bytes
        _stdin, _stdout,_stderr = client.exec_command(regex_get_swp_free_bytes)
        swap_free_bytes = _stdout.read().decode()
        
        #Rounding the Percentage
        if swap_total_bytes == "":
            swap_total_bytes = 0
            swap_percent = 0
        else:
            swap_percent = (round(float(swap_percent)))
        mem_percent = (round(float(mem_percent)))
        
        #============== Export Metrics ==============#
        
        #Memory RAM
        service_memory_usage_percent.labels(f'{hostname}', f'{host}', f'{service_scope}').set(mem_percent)
        service_memory_usage_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(mem_used_bytes)
        service_memory_total_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(mem_total_bytes)
        service_memory_free_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(mem_free_bytes)

        #Memory Swap
        service_swap_usage_percent.labels(f'{hostname}', f'{host}', f'{service_scope}').set(swap_percent)
        service_swap_usage_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(swap_used_bytes)
        service_swap_total_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(swap_total_bytes)
        service_swap_free_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(swap_free_bytes)
        
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
