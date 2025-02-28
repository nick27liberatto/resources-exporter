from prometheus_client import Enum, Gauge

#================================================#
#                 Define Metrics                 #
#================================================#   

#Ping
service_ping_msec = Gauge('service_ping_msec', 'Ping Milliseconds', ['server_hostname', 'server_ip', 'service_name', 'ping_status'])
service_ping_pkg_loss_percent = Gauge('service_ping_pkg_loss_percent', 'Ping Package Loss in Percentage', ['server_hostname', 'server_ip', 'service_name', 'ping_status'])

#Service
service_state = Enum('service_state', 'Check if service is running', ['server_hostname', 'server_ip', 'service_scope', 'service_name', 'service_pid'], 
                     states=['active', 'inactive', 'enabled', 'disabled', 'static', 'masked', 'alias', 'linked', 'failed', ''])
#Ports
service_ports_open = Gauge('service_ports_open', 'Listening ports for each server', ['server_hostname', 'server_ip', 'service_name', 'listening'])

#CPU
service_cpu_usage_percent = Gauge('service_cpu_usage_percent', 'CPU usage in percentage for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_cpu_cores = Gauge('service_cpu_cores', 'CPU quantity of cores for each Server', ['server_hostname', 'server_ip', 'service_name'])

#Network
service_network_transmitted_bytes = Gauge('service_network_transmitted_bytes', 'Network Transmitted Bytes for each Server', ['server_hostname', 'server_ip', 'service_name', 'interface'])
service_network_received_bytes = Gauge('service_network_received_bytes', 'Network Received Bytes for each Server', ['server_hostname', 'server_ip', 'service_name', 'interface'])

#Disk
service_disk_usage_percent = Gauge('service_disk_usage_percent', 'Disk usage in percentage for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_disk_usage_bytes = Gauge('service_disk_usage_bytes', 'Disk usage in bytes for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_disk_total_bytes = Gauge('service_disk_total_bytes', 'Disk size for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_disk_free_bytes = Gauge('service_disk_free_bytes', 'Disk free space in bytes for each Server', ['server_hostname', 'server_ip', 'service_name'])

#Memory RAM
service_memory_usage_percent = Gauge('service_memory_usage_percent', 'RAM usage in percentage for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_usage_bytes = Gauge('service_memory_usage_bytes', 'RAM usage in bytes for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_total_bytes = Gauge('service_memory_total_bytes', 'RAM size for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_memory_free_bytes = Gauge('service_memory_free_bytes', 'RAM free space in bytes for each Server', ['server_hostname', 'server_ip', 'service_name'])

#Memory Swap
service_swap_usage_percent = Gauge('service_swap_usage_percent', 'SWAP usage in percentage for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_usage_bytes = Gauge('service_swap_usage_bytes', 'SWAP usage in bytes for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_total_bytes = Gauge('service_swap_total_bytes', 'SWAP size for each Server', ['server_hostname', 'server_ip', 'service_name'])
service_swap_free_bytes = Gauge('service_swap_free_bytes', 'SWAP free space in bytes for each Server', ['server_hostname', 'server_ip', 'service_name'])

#================================================#
#                 Export Metrics                 #
#================================================#   

# Ping
service_ping_pkg_loss_percent.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{status}').set(pkg)
service_ping_msec.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{status}').set(msec)


# Service
service_state.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{service}', f'{pid}').state(status)

# Ports
for counter in range(len(ports)):
    service_ports_open.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{ports_services[counter]}').set(ports[counter])

# Cpu
service_cpu_usage_percent.labels(f'{hostname}', f'{host}', f'{service_scope}').set(cpu)
service_cpu_cores.labels(f'{hostname}', f'{host}', f'{service_scope}').set(cores)

# Network
for counter in range(len(network_devices)):
    service_network_transmitted_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{network_devices[counter]}').set(network_device_transmitted_bytes[counter])
    service_network_received_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}', f'{network_devices[counter]}').set(network_device_received_bytes[counter])

# Disk
service_disk_usage_percent.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_percent)
service_disk_usage_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_used_bytes)
service_disk_total_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_total_bytes)
service_disk_free_bytes.labels(f'{hostname}', f'{host}', f'{service_scope}').set(disk_free_bytes)

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
