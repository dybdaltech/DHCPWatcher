import xml.etree.ElementTree as ET
import sys, subprocess, time
from threading import Thread
from datetime import datetime
from flask import Flask
from flask import request
from flask.json import jsonify
from flask_cors import CORS
from pymongo import MongoClient

#TODO: Find a better location string for the script, (./findleases.ps1)
def Job():
    """Starts Powershell script to fetch DHCP data from the server. (Export-DHCP..)"""
    while True:
        subprocess.Popen([""])
        print("Fetched DHCP scope 10.10.0.0")
        time.sleep(60)


def leaseParse(leaseFile):
    """Parses the Lease.xml file from the Job function. Places the current date as the first object"""
    leaseArray = []
    try:
        tree = ET.parse(leaseFile)
        root = tree.getroot()
        leaseArray.append({
            "Date": str(datetime.now().date())
        })
        leases = root.findall('./IPv4/Scopes/Scope/Leases/')
        for lease in leases:
            name = lease.find('HostName')
            ipa = lease.find('IPAddress')
            macid = lease.find('ClientId')
            try:
                if(name.text):
                    leaseArray.append({
                        "IPAddress": ipa.text,
                        "Hostname": name.text,
                        "MacID" : macid.text
                    })
            except AttributeError:
                leaseArray.append({
                    "IPAddress": ipa.text,
                    "Hostname": "",
                    "MacID": macid.text
                })
        else:
            pass
    except ET.ParseError:
        print("Loading DHCP scope.. Try again later")
        return "Loading DHCP scope.. Try again later"
    return leaseArray
#Split
def leaseSave(leaseFile):
    """Basicly a copy paste from leaseParse, only saves it instead to a MongoDB instance."""
    leaseArray = []
    try:
        tree = ET.parse(leaseFile)
        root = tree.getroot()
        leases = root.findall('./IPv4/Scopes/Scope/Leases/')
        for lease in leases:
            name = lease.find('HostName')
            ipa = lease.find('IPAddress')
            macid = lease.find('ClientId')
            try:
                if(name.text):
                    leaseArray.append({
                        "IPAddress": ipa.text,
                        "Hostname": name.text,
                        "MacID" : macid.text
                    })
            except AttributeError:
                leaseArray.append({
                    "IPAddress": ipa.text,
                    "Hostname": "",
                    "MacID": macid.text
                })
        else:
            pass
    except ET.ParseError:
        print("Loading DHCP scope.. Try again later")
        return "Loading DHCP scope.. Try again later"
    return leaseArray


#Database connections:
db_client = MongoClient('', 27017) #TODO: Create seperate configuration file
db_instance = db_client.monitor
db_lease = db_instance.leases

#Print connection status for debugging, removing it later
print("connecting to MongoDB")
print("------------------")
print(db_client)
print("------------------")
print(db_instance)
print("------------------")
print(db_lease)

#Creates a seperate thread for Powershell job.
thread = Thread(target = Job)
thread.start()

#Start the web service, port: 3000. See Flask documentation on rest
app = Flask(__name__)
CORS(app)
@app.route("/")
def hello():
    return jsonify({'Devices': leaseParse('Leases.xml')})

@app.route("/save", methods=['GET', 'POST'])
def save():
    results = db_lease.insert_many(leaseSave('Leases.xml'))
    return "Leases saved!"
    
if __name__ == "__main__":
    app.run()