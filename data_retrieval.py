#!usr/local/bin/python2.7
import sys
from esmond_client.perfsonar.query import ApiConnect, ApiFilters
import datetime
import time
import calendar
import requests
import json
from math import sqrt
import collections
import ConfigParser

def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data

"""first defines the src/dest/time_start/time_end"""
#input_source = 'localhost'
"""source and destination hardwired now, can take them from the user in the future,similarly for event type"""
config=ConfigParser.ConfigParser()
config.read('test.cfg')
input_source = config.get('Section1', 'input_destination')
event_type = config.get('Section2','event_type2',0)
input_destination = config.get('Section2','input_destination2')
event_type = config.get('Section1','event_type',0)

#setting start and end times for data retrieval
time_start_local = datetime.datetime.now() - datetime.timedelta(minutes=240)
time_start_timestamp = time.mktime(time_start_local.timetuple())
time_end_local = datetime.datetime.now() - datetime.timedelta(minutes=60)
time_end_timestamp = time.mktime(time_end_local.timetuple())


"""now start query data """
filters = ApiFilters()

filters.verbose = True
filters.time_start = time_start_timestamp
filters.time_end = time.time()
#filters.tool_name = 'bwctl/iperf3'
filters.input_destination = input_destination
#filters.event_type = 'histogram-owdelay'


conn = ApiConnect('http://{0}:8085/'.format(input_source), filters) 

#md: metaData object 
#et: EventType object (base_uri, event_type, data_type, summaries)
#dpay: DataPayload object (data_type, data) 
#    dpay.data returns a list of DataPoint object or DataHistogram object
#dp: DataPoint object (ts, val, ts_epoch)

for md in conn.get_metadata():
    print md.uri
    
    et = md.get_event_type(event_type)
    if et!=None:
         break

#print et.event_type
#filters.time_end = time_end_timestamp

#summ = et.get_summary('statistics', 3600);
#print summ
#dpay = summ.get_data()

dpay = et.get_data()
jsonList = []
jsonList1 = []

"""
for dp1 in dpay.data:

    raw_data ={}
    raw_data['ts'] = '{0}'.format(str(dp1.ts))
    raw_data[str(event_type)] = '{0}'.format(str(convert(dp1.val)))

    jsonlist1.append(raw_data)
"""

for dp in dpay.data:
    min = 1e6
    max = 0
    sum = 0
    total_packets = 0
    val_list = []
    val_obj = {}
    
    for key in dp.val.keys():
        delay = float(key)
        num_packets = dp.val[key]

	#try to get raw_data into jsonList1
	val_obj[str(key)] = num_packets

        if delay<min:
            min=delay
        if delay>max:
            max=delay
        total_packets += num_packets
        sum += delay*num_packets
        for i in range(num_packets):
            val_list.append(delay)
    
    #insert val_obj into jsonList1
    raw_data = {}
    raw_data['ts'] = dp.ts_epoch
    raw_data['val'] = val_obj
    jsonList1.append(raw_data)


    val_list.sort()
    median = val_list[len(val_list)/2]
    mean = sum/total_packets
    
    variance=0
    for i in val_list:
        variance += (mean-i)*(mean-i)
    variance = variance/len(val_list)
    std_var = sqrt(variance)
    
    statistics_obj={}
    statistics_obj['standard-deviation'] = std_var
    statistics_obj['variance'] = variance
    statistics_obj['minimum'] = min
    statistics_obj['maximum'] = max
    statistics_obj['mean'] = mean
    statistics_obj['median'] = median
    
    obj ={}
    obj['time'] = '{0}'.format(str(dp.ts))
    obj['statistics'] = statistics_obj
   
    jsonList.append(obj)

    
# saves the data in json format on the vm
with open('/home/sdn/raw_data.txt', 'w') as outfile1:
    json.dump(jsonList1, outfile1)
with open('/home/sdn/stats.json', 'w') as outfile:
    json.dump(jsonList, outfile)


print("Hello World, from Python!")
