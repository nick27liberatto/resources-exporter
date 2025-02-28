#Optional Connection Configuration
shell_cmd_get_local_user = "echo $USER | tr -d '\n'"

#Service
regex_service_name = "%s.*.service.*enabled"
shell_cmd_service_qnt = "systemctl list-unit-files | grep -Po '%s' | wc -l"
shell_cmd_get_service = "systemctl list-unit-files | grep -Po '%s' | sed -n '%sp' | awk '{print $1}' | tr -d '\n'"
shell_cmd_get_status = "systemctl status %s | grep -Po '(?<=Active:.)\w+' | tr -d '\n'"
shell_cmd_get_pid = "systemctl status %s | grep -Po '(?<=PID:.)\w+' | tr -d '\n'"

#Ping
shell_cmd_get_pkg = "ping -c 5 -i 0.2 %s | grep -Po '(?<=received, )\w+' | tr -d '\n'"
shell_cmd_get_msec = "ping -c 1 -W 3 %s | grep -Po '(?<=time=)[0-9]+.[0-9]+' | tr -d '\n'"

#Ports
shell_cmd_ports_qnt = "nmap %s | grep -P '\d+/' | wc -l"
shell_cmd_get_ports_services = "nmap %s | grep -P '\d+/' | awk '{print $3}' | sed -n '%sp' | tr -d '\n'"
shell_cmd_get_ports = "nmap %s | grep -Po '\d+/' | tr -d '/' | sed -n '%sp' | tr -d '\n'"


#CPU
shell_cmd_get_cpu = "echo $[100-$(vmstat 1 2|tail -1|awk '{print $15}')] | tr -d '\n'"
shell_cmd_get_cores = "cat /proc/cpuinfo | grep 'cpu cores' | sed -n 1p | awk '{print $4}'"
        
#Network
shell_cmd_devices_qnt = "ip -s link | grep -Po '(?<=\d:\s)\w+' | wc -l"
shell_cmd_get_devices = "ip -s link | grep -Po '(?<=\d:\s)\w+' | sed -n '%sp' | tr -d '\n'"
shell_cmd_tx_rx_qnt = "ip -s link | awk '{print $1}' | grep -P '\d+$' | wc -l"
shell_cmd_get_tx_rx_bytes = "ip -s link | awk '{print $1}' | grep -P '\d+$' | sed -n '%sp' | tr -d '\n'" 

#Disk '/' for Other Resources
shell_cmd_get_disk = "df | grep -P '/$' | awk '{print $%s}' | tr -d '%%' | tr -d '\n'"

#Disk '/opensearch' for OpenSearch
shell_cmd_get_disk_opensearch = "df | grep opensearch | awk '{print $%s}' | tr -d '%%' | tr -d '\n'"

#DIsk '/data/backup' for MongoDB
shell_cmd_get_disk_mongodb = "df | grep mongodb | awk '{print $%s}' | tr -d '%%' | tr -d '\n'"

#Memory RAM
shell_cmd_get_mem_usage_percent = "free | grep Mem | awk '{print ($3/$2)*100}' | tr -d '\n'"
shell_cmd_get_mem_total_bytes = "free | grep Mem | awk '{print $2}' | tr -d '\n'"
shell_cmd_get_mem_used_bytes = "free | grep Mem | awk '{print $3}' | tr -d '\n'"
shell_cmd_get_mem_free_bytes = "free | grep Mem | awk '{print $4}' | tr -d '\n'"

#Memory Swap
shell_cmd_get_swp_usage_percent = "free | grep Swap | awk '{print ($3/$2)*100}' | tr -d '\n'"
shell_cmd_get_swp_total_bytes = "free | grep Swap | awk '{print $2}' | tr- d '\n'"
shell_cmd_get_swp_used_bytes = "free | grep Swap | awk '{print $3}' | tr -d '\n'"
shell_cmd_get_swp_free_bytes = "free | grep Swap | awk '{print $4}' | tr -d '\n'"

