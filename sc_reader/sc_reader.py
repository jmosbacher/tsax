
import xe1tscwebapi as sc
import os
import time 
import re
# import datetime
from influxdb import InfluxDBClient

user = os.environ["SCUSER"]
password = os.environ["SCPASS"]

mysc = sc.xe1tscwebapi()

mysc.AuthUser(user,password)
last_login = time.time()
units = {}
names = []
descs = {}

with open('/config/scvariables.dat', 'r') as ff:
    for l in ff:
        if l.startswith('#'):
            continue
        try:
            name,unit,desc = l.rstrip().split(',')
            units[name]=unit
            names.append(name)
            descs[name]=desc
        except:
            print ('\nWarning: find an empty or incomplete line! Check your scvariable.dat file\n')
            print(l.rstrip().split(','))

query = {'name':'XE1T.CRY_PT103_PCHAMBER_AI.PI',
               'QueryType':'lab',
            #    'StartDateUnix':'1483056000',
            #    'EndDateUnix':'1483056900',
            #    'Interval':'5'
              }


client = InfluxDBClient(host='influxdb', port=8086)
dbs = client.get_list_database()
if "sc" not in [d['name'] for d in dbs]:
    client.create_database("sc")


def log_values(data,db='sc'):
    json_body = [
        {"measurement": name,
        "time":ts,
        "fields": {"value": value,
                    "description": descs[name],
                    "unit":units[name]}
    }
    for name,ts,value in data]
    print('logging values to {} DB'.format(db))
    client.write_points(json_body,  time_precision='s',database=db)
try:
    while True:
        data = []
        now = time.time()
        if (now-last_login)>3600:
            mysc.AuthUser(user,password)
            last_login = time.time()

        for name in names:
            query['name'] = name
            mysc.SetQuery(query)
            mydata = mysc.GetSCLastValue()[0]
            data.append((name,mydata['timestampseconds'],mydata['value']))
        log_values(data, db='sc')

        # query['name'] = 'PMT'
        # query['QueryType'] = 'pmt'
        # mydata = mysc.GetSCLastValue()
        # data = [(d['tagname'],d['timestampseconds'],d['value']) for d in mydata]
        # log_values(data, db='pmt')
        time.sleep(5)

except KeyboardInterrupt:
    pass