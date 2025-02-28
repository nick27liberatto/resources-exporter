import csv

class Settings:
    def __init__(self, instance, service, hostname):
        self.instance = instance
        self.service = service
        self.hostname = hostname
        
    def arrange_data(self):
        return self.instance, self.service, self.hostname

def data():
    data = []
    with open('./host/host.csv') as h:
        csv_reader = csv.reader(h)
        for index, row in enumerate(csv_reader):
            server = Settings(row[0], row[1], row[2])
            data.append(server.arrange_data())
        return data