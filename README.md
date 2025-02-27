# **Resources Exporter Script**

Script to monitor the hardware and services of linux based systems, and export metrics to Prometheus.

### Dependencies to run script

- [python3](https://www.python.org/)
- [paramiko](https://www.paramiko.org/)
- [prometheus_client](https://github.com/prometheus/client_python)

### Dependencies for host system

- [OpenSSH](https://www.openssh.com/)
- [Systemd](https://systemd.io/)

## How it works?

**1.** Initialize variables, create regex filters and Prometheus metrics;

**2.** Read each row of the `host.csv`, storing the values in lists based on the columns index;
<br><br>
`IP,SERVICE,ALIAS/HOSTNAME`
<br>

**3.** Loop through the list that contain the servers IP, connect via SSH with Paramiko Library and proceed to execute the filtered commands created above;

**4.** With prometheus_client library, setup the data to a valid Prometheus metric format;

**5.** Expose the server to desired port.

## How to configure?

In order to the script work properly, it's necessary to configure some components that impact direct and indirectly on the routine that the script will follow.

**1.** Define the target instances that you need to monitor in the `./host/host.csv` file:
<br><br>
&emsp;&emsp;Example: `10.41.0.0,mongo,mongo-server-01`
<br><br>
&emsp;&emsp;Pattern: `IP,SERVICE,ALIAS_or_MACHINE_HOSTNAME`

>***Note: You don't need to insert the full service name, just the prefix and the regular expression will figure it out.***

>***Warning: You need to use the .csv syntax (Just commas to separate each field).***

**2.** On the footer of the script, define the desired port you want to expose:
<br><br>
&emsp;&emsp;Example:<br>

```
if __name__ == '__main__':
    start_http_server(9095)
    print("Exporter running at http://localhost:9095")

    while True:
        setup()
        time.sleep(5)
```

**3. SSH Keys**<br><br>
&emsp;&emsp; The procedure used to get authentication for the ssh connection is through **public keys**.

&emsp;&emsp;3.1. Generate the Keys for the server who will fetch the metrics:

&emsp;&emsp; `ssh-keygen -t rsa -b 4096`

&emsp;&emsp;3.2. Verify if the keys are in the path: `~/.ssh/`. If not, copy then there.

&emsp;&emsp;3.3. Copy the `id_rsa.pub` to the file `~/.ssh/authorized_keys` of every server you want to monitor. 

&emsp;&emsp;*3.3.1. It's fine to execute this step manuallly, but to speed things up. You can just execute the script `add_ssh_key_tool.sh` to conclude.*

**4. LoadBalancer (Haproxy):**<br><br>
&emsp;&emsp; In the `/etc/haproxy/haproxy.cfg`, configure a backend listener for the instance that will run the script.

&emsp;&emsp; Example:
```
#Scripts Monitoring {Environment} <- (QA, PRD, CTOS, etc..)
backend scripts-monitoring-{environment} # Take off the '{}'
server VHLNX000 192.168.0.1:8080
```
&emsp;&emsp;Pattern: `server {MACHINE_HOSTNAME} {IP_ADRESS}:{DEFINED_PORT}`

**5. Metrics (Prometheus):**<br><br>
&emsp;&emsp; In the `/etc/prometheus/prometheus.yml` configure the job for the resources-exporter script.

&emsp;&emsp; Example:

```
#Scripts Monitoring {Environment}
  - job_name: "resources-exporter-{environment}" # Take off the '{}'
    static_configs:
     - targets:
        - '192.168.0.1:8080'
       labels:
         alias: "common-services"
```

&emsp;&emsp;Pattern: `- '{IP}:{DEFINED_PORT}'`

>***Warning: Pay attention on the indentation. The block `- job_name` must be under/inside `scrape_configs:`.***

**6. Service Manager Tool (Systemd):**<br><br>
&emsp;&emsp; Inside the server who will run the service, go to `/etc/systemd/system/` create a file called `resources-exporter.service`. Then, define the how the service will behave on the system.

&emsp;&emsp; Example:

```
[Unit]
Description=Resources Exporter
After=network.target

[Service]
User=infra
WorkingDirectory=/home/infra/scripts_devops/monitoring/exporter/
ExecStart=/usr/bin/python /home/infra/scripts_devops/monitoring/exporter/resources_exporter.py
Restart=always

[Install]
WantedBy=multi-user.target                   
```
 
## How to run?

**1.** Inside the server that will run the service, enable and start the service with systemctl:

&emsp;&emsp;3.1. `systemctl enable resources-exporter.service` 

&emsp;&emsp;3.2. `systemctl start resources-exporter.service` 

&emsp;&emsp; To monitor the current state of the service, run:

&emsp;&emsp;3.2. `systemctl status resources-exporter.service` 

&emsp;&emsp; *or*

&emsp;&emsp;3.2. `journalctl -u resources-exporter.service | tail -60`

## How to test?

**1. Resources Exporter Script and Haproxy:**

In order to test, acess via browser or prefered tool the IP of the server that is running the service, plus the defined Port.

Example:
http://10.41.0.0:9095/

If you see metrics such as **'CPU, Memory, Network'**, the custom exporter and Haproxy configuration are working.

**2. Prometheus Scraping:**

In the browser, acess the Prometheus Web Interface and attempt some queries. With the results, check in the font if they are correct. If so, everything is properly working.

Example: `sum by (server_ip, service_name) (service_disk_free_bytes)`.