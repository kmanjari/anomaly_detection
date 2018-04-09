import json
import pandas as pd
#import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
from numpy import linspace
import numpy as np
from datetime import datetime
import matplotlib
import sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import re
import ConfigParser
#from Constants import *


with open('stats.json','r') as f:
     data = json.load(f)

#function to flatten json data

def flatten_json(y):
    out = {}

    def flatten(x, name =''):
        if type(x) is dict:
           for a in x:
               flatten(x[a], name +a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1 
        else:
            out[str(name[:1])] = str(x)
    flatten(y)
    return out

#flat = flatten_json(data)
config=ConfigParser.ConfigParser()
config.read('test.cfg')
input_source = config.get('Section1', 'input_destination')
input_destination = config.get('Section2', 'input_destination2')

#gives the json data in terms of row and columns

data1 = json_normalize(data)

temp_array = []
temp_array = data1

owdelay= temp_array[temp_array.columns[2:4] | temp_array.columns[6:7]]


print owdelay

num_samples = len(temp_array.index)

MIN_NUM_INPUT_SAMPLES = 20

if num_samples < MIN_NUM_INPUT_SAMPLES :
   print 'Error: Too few samples'

print temp_array
#PD process

swc = 120
sens = 2
td = 80
trig_cnt = 0

sum_buff = pd.DataFrame(0,index= np.arange(swc), columns =['buff_Values'])
#initializing summary buffer


#for i in range(0,swc-1):
#    sum_buff.ix[i, 1:2]= owdelay.ix[i,1:2]
sum_buff['buff_Values'] = owdelay.reindex(index=sum_buff.index, columns = ['statistics.median'])

# initialize trigger buffer

#print sum_buff
trig_buff = pd.DataFrame(0, index = np.arange(td), columns=['Values_trig_buff'])

mu_sum_buff = sum_buff["buff_Values"].mean()
std_sum_buff = sum_buff['buff_Values'].std()

last_detect = 0
timer = 0

T_sl = mu_sum_buff - sens*std_sum_buff
T_su = mu_sum_buff + sens*std_sum_buff

detect_times = pd.DataFrame(0, np.arange(num_samples), columns =['Values'])


num_detect = 0
detect_times.ix[1, 0:1]=0
#temp_array = temp_array.values

#temp_array.apply(lambda x: pd.to_numeric(x, errors = 'ignore'))
temp_track = pd.DataFrame(index = np.arange(len(owdelay)),columns =['statistics.median', 'mean of summary buffer', 'time'])

for i in range(swc,len(owdelay)):
    sample = owdelay.iloc[i, 1:2]
    g = sample.item()
    
    temp_track.iloc[i, 0:1] = temp_array.iloc[i, 2:3]
    temp_track.iloc[i, 2:3] = temp_array.iloc[i, 6:7]         
   
    if last_detect == 0:
       if  g <= T_su.item():
          #No Event (NE) state
          #add new sampke into summary buffer, and update
          for j in range(2,swc):
              sum_buff.ix[(swc-j), :1] = sum_buff.ix[swc-j+1, :1]
              sum_buff.ix[swc-1, 0:1] = sample
              mu_sum_buf = sum_buff.mean()
              std_sum_buff = sum_buff.std()
              T_sl = mu_sum_buff - sens*std_sum_buff
              T_su = mu_sum_buff + sens*std_sum_buff

# decrease the number of trigger buffer by one
#put the latest trig buff data into summary buff
          if trig_cnt > 0:
             for j in range(0, swc-2):
                 sum_buff.ix[j , 0:1] = sum_buff.ix[j+1, 0:1]
             sum_buff.ix[swc, 0:1] = trig_buff.ix[trig_cnt, 0:1]
             trig_cnt = trig_cnt - 1

          if trig_cnt == 0:
             trig_buff = pd.DataFrame(0, index = np.arange(td), columns = ['Values_trig_buff'])

       else: 
#put into trigger buffer
             trig_cnt = trig_cnt + 1
             trig_buff.ix[trig_cnt, 0:1] = sample

#             if (trig_cnt >= 0.75*td && trig_cnt<td):

#event impeding state(EI)
             if (trig_cnt == td):
                   T_su = 1.2 * trig_buff.max()
                   T_sl = 0.8 * trig_buff.min()

                   last_detect = 1
                   trig_cnt = 0

                   for j in range(1, trig_cnt):
                        sum_buff.ix[swc- trig_cnt +j, 0:1] = trig_buff[j, 0:1]

                   timer = timer +1
                   num_detect = num_detect + 1
                   detect_times.ix[num_detect, 0:1] = i

    else:
        if g > T_su.item():
#new detect
           trig_buff = pd.DataFrame(0, index = np.arange(td), columns = ['Values'])
           trig_buff.ix[1, 0:1] = sample
           last_detect = 1
           trig_cnt = 0
           timer = 0
           timer = timer + 1
           num_detect = num_detect + 1
           detect_times.ix[num_detect, 0:1] = i

           T_su = 1.2 * trig_buff.max()
           T_sl = 0.8 * trig_buff.max()
 
        else:
            timer = timer + 1
#return to NE state
        if timer == swc:     
           mu_sum_buff = sum_buff.mean()
           std_sum_buff = sum_buff.std()
           last_detect = 0
           timer = 0
           T_sl = mu_sum_buff - sens*std_sum_buff
           T_su = mu_sum_buff + sens*std_sum_buff

           trig_buff = pd.DataFrame(0, index = np.arange(td), columns =['Values'])
    
    mu_sum_buff = sum_buff['buff_Values'].mean()
    std_sum_buff = sum_buff['buff_Values'].std()
    temp_track.ix[i, 1:2] = mu_sum_buff

#print temp_track


#defines RGB colour scheme for the matlab plots generated later.
tableau20 = [(35,119,180), (255,127,14), (158,218,229), (199,199,199), (44,160,125), (152,223,228)]
for i in range(len(tableau20)):
    r,g,b = tableau20[i]
    tableau20[i] = (r / 255., g / 255., b / 255.)

print(detect_times)

plt.figure(1)
plt.xticks(fontsize=8)
ax1 = plt.subplot(111)

ax1.spines["top"].set_visible(False)

ax1.spines["right"].set_visible(False)

#Removes white spaces. 
ax1.get_xaxis().tick_bottom()
ax1.get_yaxis().tick_left()

#DF1=pd.concat([temp_track['statistics.median'], temp_track['mean of summary buffer'], temp_track['time']], axis = 1)
DF2=temp_track.ix[(swc):]
DF3 = owdelay.ix[(swc):]
#plt.yticks(linspace(10.00,20.00,2), [str(x) + "" for x in linspace(10.00, 20.00,2)], fontsize=8)
plt.tick_params(axis='both', which = 'minor', labelsize = 10)

plt.tick_params(axis = "both", which = "both", bottom = "off", top = "off", labelbottom = "on",
                left = "on", right = "on", labelleft = "on")
ll = DF2['mean of summary buffer'].loc[DF2['mean of summary buffer'].idxmin()]
#print ll
plt.ylim((ll-2),(ll + 5))
print DF2

#print owdelay
major = ['statistics.median', 'mean of summary buffer']
#plt.title("Perfsonar Anomaly detection")
time_format = '%Y-%m-%d %H:%M:%S'
time = [datetime.strptime(i, time_format) for i in DF2['time']]
plt.tick_params(axis='both', which = 'minor', labelsize = 6)

ax1.xaxis.set_minor_locator(dates.MinuteLocator(byminute=None,interval=10))

ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M:%S'))
ax1.xaxis.grid(True, which = "minor")
ax1.yaxis.grid()
ax1.xaxis.set_major_locator(dates.MonthLocator())
ax1.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b-%d\n%Y'))
plt.figtext(0.5, 0.8, "Number of anomalies Detected= %s"%num_detect, fontsize = 7)
plt.title("Plateau Detection Algorithm running between nodes %s and %s"%(input_source,input_destination), fontsize = 8)
for rank,column in enumerate(major):
    plt.plot(time, DF2[column.replace("\n", "")].values, lw = 0.75, color = tableau20[rank])
#    plt.plot(time, DF3[column.replace("\n", "")].values, lw = 0.75, color = tableau20[rank])
    plt.legend(major, loc = "best", prop = {"size": 8})
    plt.savefig('fig1')
#    for rank,column in enumerate(major1):
#        plt.plot(time, temp_track[column.replace("\n", "")].values, lw = 0.75, color = tableau20[rank])
#        plt.legend(major1, loc = "best" , prop ={"size": 8})
#        plt.savefig("fig1")


#plt.plot(owdelay.ix[start_index:stop_index, :2])
#plt.savefig('fig2')

#plt.plot(temp_track.ix[start_index:stop_index, :2])
#plt.savefig('fig3')
