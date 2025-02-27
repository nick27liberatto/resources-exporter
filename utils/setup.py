import csv

class Settings:
    def __init__(self, instance, service, hostname):
        self.instance = instance
        self.service = service
        self.hostname = hostname
        
    def arrange_data(self):
        print(f"""
        
        instance: {self.instance}
        service: {self.service}
        hostname: {self.hostname}
        
        """)

#Get Hosts from CSV File 'host.csv'
def get_hosts():
    with open('../host/host.csv') as h:
        csv_reader = csv.reader(h)
        for index, row in enumerate(csv_reader):
            server = Settings(row[0], row[1], row[2])
            server.arrange_data()
    
get_hosts()


#=======================================#
#               Variables               #
#=======================================#

#Host Configuration
# IP = 0
# SERVICE = 1
# HOSTNAME = 2
# vm_ips = []
# vm_services = []
# vm_hostnames = []

#=======================================#
#                 Setup                 #
#=======================================#