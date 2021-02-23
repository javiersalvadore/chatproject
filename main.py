import pandas as pd
import plotly.graph_objects as go
import os
import plotly.express as px
import datetime
import calendar
import numpy as np
from dateutil import parser
#from tkinter import filedialog
#from tkinter import *
start = datetime.datetime.now()

if not os.path.exists("images"):
    os.mkdir("images")

def clean_time(date):
    hour = ''
    if int(date[3:]) <= 15:
        hour = date[0:2] + ':00'
    elif int(date[3:]) <= 45:
        hour = date[0:2] + ':30'
    elif int(date[3:]) >= 45 and int(date[0:2]) == 23:
        hour = '00:00'
    else:
        hour = str(int(date[0:2])+1) + ':00'
    if len(hour) < 5:
        return '0' + hour
    else:
        return hour

def dayNameFromWeekday(weekday):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[weekday]

'''def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)

root = Tk()
folder_path = StringVar()
lbl1 = Label(master=root,textvariable=folder_path)
lbl1.grid(row=0, column=1)
button2 = Button(text="Browse", command=browse_button)
button2.grid(row=0, column=3)
mainloop()
'''
#location = folder_path.get() + r'\result.json'

rawchat = pd.read_json('result.json')
chat = rawchat.iloc[1][1][0]['messages']

# Define Dataframe with the json messages list of dicts, strip it from system messages and then define usernames in the chat

chatdata = pd.DataFrame(chat)

names, timeslist = [], []
cleanchat = chatdata.drop(chatdata[chatdata.type == 'service'].index)

cleanchat = cleanchat.rename(columns={'from': 'name'})
cleanchat = cleanchat.reset_index()
cleanchat = cleanchat.drop(labels='id', axis=1)
cleanchat['newdate'] = cleanchat['date'].str.slice(11, 16)
cleanchat['newdate'] = cleanchat['newdate'].apply(func=clean_time)
cleanchat['proper_date'] = pd.to_datetime(cleanchat['date'], format='%Y-%m-%dT%H:%M:%S')
cleanchat['day_name'] = cleanchat['proper_date'].apply(func=datetime.datetime.weekday)
cleanchat['day_name'] = cleanchat['day_name'].apply(func=dayNameFromWeekday)

for element in range(chatdata.shape[0]):
    if len(names)<2:
        if chatdata.loc[element]['from'] not in names:
            names.append(chatdata.loc[element]['from'])
    else:
        break

for element in range(cleanchat.shape[0]):
    if len(timeslist)<48:
        if cleanchat.loc[element]['newdate'] not in timeslist:
            timeslist.append(cleanchat.loc[element]['newdate'])

timeslist = sorted(timeslist)
# Set up dataframes for each user's sent messages and
# clean up time structures

timings = {i: {date: 0 for date in timeslist} for i in names}
dayfreq = {i: {day: 0 for day in calendar.day_name} for i in names}

for element in cleanchat.iterrows():
    timings[element[1]['name']][element[1]['newdate']] += 1
    dayfreq[element[1]['name']][element[1]['day_name']] += 1


useronechat = cleanchat.drop(cleanchat[cleanchat.name == names[0]].index)
usertwochat = cleanchat.drop(cleanchat[cleanchat.name == names[1]].index)

# Set out graphical representations of the data

fig = go.Figure()
fig.add_trace(go.Bar(
    x=timeslist,
    y=list(timings[names[0]].values()),
    name=names[0],
    marker_color='lightsalmon'
))
fig.add_trace(go.Bar(
    x=timeslist,
    y=list(timings[names[1]].values()),
    name=names[1],
    marker_color='#C1C6FC'
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig.update_layout(barmode='group', xaxis_tickangle=-45)

fig.write_html("graph.html")
fig.write_image("graph.svg")

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=list(calendar.day_name),
    y=list(dayfreq[names[1]].values()),
    name=names[1],
    marker_color='#C1C6FC'
))
fig2.add_trace(go.Bar(
    x=list(calendar.day_name),
    y=list(dayfreq[names[0]].values()),
    name=names[0],
    marker_color='lightsalmon'
))

# Here we modify the tickangle of the xaxis, resulting in rotated labels.
fig2.update_layout(barmode='group', xaxis_tickangle=-45)

fig2.write_html("graph2.html")
fig2.write_image("graph2.svg")

fig3 = go.Figure(data=[go.Pie(labels=names, values=[len(range(useronechat.shape[0])), len(range(usertwochat.shape[0]))])])
fig3.write_html("graph3.html")
fig3.write_image("graph3.svg")
#print(useronechat.iloc[:50]['newdate'])

end = datetime.datetime.now()
print(end-start)