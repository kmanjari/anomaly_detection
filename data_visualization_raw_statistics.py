import json
import pandas as pd
import pandas
import sys
import matplotlib
matplotlib.use('Agg')
#import Tkinter as tk
#sys.modules['tkinter'] = Tkinter
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
from numpy import linspace
import numpy as np
from datetime import datetime
import matplotlib.dates as dates
with open('new1.json', 'r') as f:
    data = json.load(f)
# flattens json dat as there is a dictionary within a dictionary
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten( x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[str(name[:-1])] = str(x)

    flatten(y)
    return out

flat = flatten_json(data)

data1 = json_normalize(data)
print data1

tableau20 = [(35, 119, 180), (255, 127, 14), (158, 218, 229), (199, 199, 199), (44, 160, 125), (152, 223, 228)]
for i in range(len(tableau20)):
    r,g,b = tableau20[i]
    tableau20[i] = (r / 255., g / 255., b / 255.)


plt.figure(1)
plt.xticks(fontsize=8)
ax1 = plt.subplot(111)

ax1.spines["top"].set_visible(False)
# ax1.spines["bottom"].set_visible(False)
ax1.spines["right"].set_visible(False)
# ax1.spines["left"].set_visible(False)
ax1.get_xaxis().tick_bottom()
ax1.get_yaxis().tick_left()
# removes unnecessary white space

plt.yticks(linspace(92.00, 100.00, 10), [str(x) + "" for x in linspace(92.00, 100.00, 10)], fontsize=8)
plt.tick_params(axis='both', which='minor', labelsize=10)


plt.tick_params(axis="both", which="both", bottom="off", top="off", labelbottom="on",
                left="off", right="on", labelleft="on")


major = ['statistics.maximum', 'statistics.mean', 'statistics.median', 'statistics.minimum']

plt.title("Perfsonar statistics for one way delay")
time_format = '%Y-%m-%d %H:%M:%S'
time = [datetime.strptime(i, time_format) for i in data1['time']]
print time
plt.tick_params(axis='both', which='minor', labelsize=8)
ax1.xaxis.set_minor_locator(dates.MinuteLocator(byminute=None,
                                                interval=10))
ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M:%S'))
ax1.xaxis.grid(True, which="minor")
ax1.yaxis.grid()
ax1.xaxis.set_major_locator(dates.MonthLocator())
ax1.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b-%d\n%Y'))

for rank, column in enumerate(major):

    plt.plot(time, data1[column.replace("\n", "")].values, lw=0.75, color=tableau20[rank])
    plt.legend(major, loc="upper right", prop={"size": 8})
    plt.savefig("datavisualization")


plt.figure(2)
plt.xticks(fontsize=8)
ax2 = plt.subplot(111)
ax2.spines["top"].set_visible(False)
# ax.spines["bottom"].set_visible(False)
ax2.spines["right"].set_visible(False)
# ax.spines["left"].set_visible(False)
ax2.get_xaxis().tick_bottom()
ax2.get_yaxis().tick_left()
# removes unnecessary white space
plt.tick_params(axis='both', which='minor', labelsize=8)

plt.tick_params(axis="both", which="both", bottom="off", top="off", labelbottom="on",
                left="off", right="on", labelleft="on")
plt.title("Perfsonar Statistics for one way delay")

minor = ['statistics.standard-deviation', 'statistics.variance']

ax2.xaxis.set_minor_locator(dates.MinuteLocator(byminute=None,
                                                interval=10))
ax2.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))
ax2.xaxis.grid(True, which="minor")
ax2.yaxis.grid()
ax2.xaxis.set_major_locator(dates.MonthLocator())
ax2.xaxis.set_major_formatter(dates.DateFormatter('\n\n\n%b-%d\n%Y'))

for rank, column in enumerate(minor):

    plt.plot(time, data1[column.replace("\n", "")].values, lw=0.75, color=tableau20[rank])
    plt.legend(minor, loc="upper right", prop={"size": 8})
    plt.savefig("data visualization2")
