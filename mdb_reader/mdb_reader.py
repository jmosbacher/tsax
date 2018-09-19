from pymongo import MongoClient
import os
from influxdb import InfluxDBClient
import time
import datetime


mongopwd = os.environ["MONGOPASS"]
mongourl = "mongodb://pax:{}@xenon1t-daq.lngs.infn.it:27017/run".format(mongopwd)
client = InfluxDBClient(host='influxdb', port=8086,)


dbs = client.get_list_database()
print(dbs)
if "mdb" not in [d['name'] for d in dbs]:
    client.create_database("mdb")

last_run: int = 9227
last_date = datetime.datetime(2018, 5, 2, 16, 32, 28)
last = client.query('SELECT LAST("value"),"time" from "tpc_event_rate"', database='mdb').get_points()
last = list(last)
if last:
    # last_date = datetime.datetime.fromtimestamp(last[0]['time'])
    last_date = datetime.datetime.strptime(last[0]['time'],"%Y-%m-%dT%H:%M:%SZ")
print("last date:   ",last_date)
coll = MongoClient(mongourl)['run']['runs_new']
def write_data(name, data):
    json_body = [{
                "measurement":name,
                "time": int((entry['srun']+0.5*(entry['erun']-entry['srun'])).timestamp()),
            "fields":{"value": entry['event_rate'],
            "run_number":entry['number']},
            } for entry in data]

    client.write_points(json_body,  time_precision='s',database='mdb')

try:
    while True:
        print('Connecting to DB')
        # TPC rates
        aggregate_cursor = list(coll.aggregate([
            {"$match": {"detector": "tpc", "end": {"$exists": True}, "trigger.events_built": {"$gt": 1000}, "start":{"$gt":last_date},"reader.ini.name": "background_stable"}},
            {"$sort": {"number": 1}},
            {"$project": {"number":"$number","srun": "$start","erun": "$end", "event_rate": {"$divide": ["$trigger.events_built", {"$multiply": [.001, {"$subtract": ["$end", "$start"]}]}]}}}
            ]))
        print('Got back tpc data for {} runs.'.format(len(aggregate_cursor)))
        #print(aggregate_cursor[:2])
        if aggregate_cursor:
            print("saving tpc data data to mdb DB")
            write_data("tpc_event_rate", aggregate_cursor)
            # last_run = aggregate_cursor[-1]["number"]
            last_date = aggregate_cursor[0]["srun"]
        # Muon veto rates
        aggregate_cursor_mv = list(coll.aggregate([
            {"$match": {"detector": "muon_veto", "end": {"$exists": True},"start":{"$gt":last_date}, "trigger.events_built": {"$gt": 1000},"reader.ini.name": "muon_mode_sync_triggersentTPC"}},
            {"$sort": {"number": 1}},
            {"$project": {"number":"$number","srun": "$start","erun": "$end", "event_rate": {"$divide": ["$trigger.events_built", {"$multiply": [.001, {"$subtract": ["$end", "$start"]}]}]}}}
            ]))
        print('Got back muVeto data for {} runs.'.format(len(aggregate_cursor_mv)))
        if aggregate_cursor_mv:
            print("saving muVeto data data to mdb DB")
            write_data("mv_event_rate",aggregate_cursor_mv)
            last_date = aggregate_cursor_mv[0]["srun"]
            #print(aggregate_cursor_mv[:2])
        time.sleep(60)
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)

