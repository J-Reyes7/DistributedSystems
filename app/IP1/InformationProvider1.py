import socket
import threading
import yfinance as yf
import sqlite3
import numpy as np
import pandas as pd
import pickle
import numpy
import os
import time
from shutil import copyfile
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

global_counter = 0

IP1_port = 5001
IP2_port = 5002
IP3_port = 5003


format = 'utf-8'
header = 64 
host_ip = socket.gethostbyname(socket.gethostname())
disconnect_msg = '!disconnnect'
# create socket
socket_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
location = (host_ip, IP1_port)
# bind socket
socket_server.bind(location)

db = sqlite3.connect('../phase2.db')
# subscriber_df.to_sql('subsciber',db,if_exists='replace',index=True,index_label='subs')
# filteredmsg_df.to_sql('filtered',db,if_exists='replace',index=True,index_label='subs')
columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Ads']
zeros = np.zeros((1,len(columns)))
df = pd.DataFrame(zeros,index=[['initialize'],['MultiIndex']],columns = columns)
df.index.names = ['sub ID','publisher']
df.loc[:,:] = False
df.loc[:,'Ads'] = True
subscribers = []

def SendToIP2(event):
    # create socket
    socket_IP1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    IP2_location = (host_ip, IP2_port)
    socket_IP1_location = (host_ip,IP1_port)
    # bind socket
    socket_IP1.bind(socket_IP1_location)
    # connect publisher socket to IP1
    socket_IP1.connect(IP2_location) 
    # serialize the pandas Series object into a string representation
    msg = pickle.dumps(event)
    # get length of string representation
    msg_length = len(msg)
    # convert message length to a string and encode it using utf-8
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    # send message length 
    socket_IP1.send(send_length)
    # send message
    socket_IP1.send(msg)

def SendToIP3(event):
    # create socket
    socket_IP1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    IP3_location = (host_ip, IP3_port)
    socket_IP1_location = (host_ip,IP1_port)
    # bind socket
    socket_IP1.bind(socket_IP1_location)
    # connect publisher socket to IP1
    socket_IP1.connect(IP3_location) 
    # serialize the pandas Series object into a string representation
    msg = pickle.dumps(event)
    # get length of string representation
    msg_length = len(msg)
    # convert message length to a string and encode it using utf-8
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    # send message length 
    socket_IP1.send(send_length)
    # send message
    socket_IP1.send(msg)

# returns rendezvous node responsible for notifying 
# subinfo need to include subscriber address before sending to correct broker
# do for each subscribe or unsubscribe from web UI thread
def SN(subinfo):
    data, topics, length = filter_msg_data(subinfo)  # LIST OF TRUE/FALSE VALUES IN ORDER
    # topics = numpy.array(topics)
    # subscriber = data.get('username', None).lower()
    getTicker = data.get('content', None).upper()
    # getTicker = subinfo[0]
    if getTicker == 'AAPL':
        return ['IP1']
    elif getTicker == 'LYFT':
        return ['IP2']
    elif getTicker == 'AMZN':
        return ['IP3']

# I put this in the app part so when the sub subscribes, then the sn will be called
# rvlist = SN(subinfo)
#
# if 'IP1' in rvlist:
#     df = addNewSubscriberToDf(df, username)
#     pass # use subscription info to update dataframe like you did in phase 2
# elif 'IP2' in rvlist:
#     SendToIP2(subinfo)
# elif 'IP3' in rvlist:
#     SendToIP3(subinfo)






def addNewSubscriberToDf(df, username):
    df.loc[(username,'AAPL'),:] = False
    df.loc[(username,'AAPL'),'Ads'] = True

    df.loc[(username, 'LYFT'), :] = False
    df.loc[(username, 'LYFT'), 'Ads'] = True

    df.loc[(username, 'AMZN'), :] = False
    df.loc[(username, 'AMZN'), 'Ads'] = True

    # subscribers.append(username)

    return df

def unadvertise(df, subscriber, ticker):
    df.loc[(subscriber, ticker),'Ads'] = False
    # df.loc[(subscriber, ticker,),'Ads'] = False
    return df

def unsubscribe(df, subscriber, ticker):
    df.loc[(subscriber, ticker), :] = False
    return df


tickers = ['AAPL']
raw_msg_df = pd.DataFrame(columns=tickers)

filtered_msg_df = pd.DataFrame(columns = tickers)
def handle_publisher_ip(socket_data, source):
    # handles the individual connections between a client and a server
    print('[new connection] ip: %s  port: %s connected.' % (source[0],source[1]))
    while True:
        msg_length = socket_data.recv(header).decode(format)
        
        if msg_length: 
            msg_length = int(msg_length)
            msg = socket_data.recv(msg_length)
            event = pickle.loads(msg)
            if type(test) is type(pd.Series([])):
                ticker = event.name
                raw_msg_df[ticker] = event

                # Append subscribers to list
                for e in df.index.values:
                    if e[0] not in subscribers:
                        subscribers.append(e[0])

                for sub in subscribers:
                    raw = (raw_msg_df[ticker].to_frame()).transpose().loc[ticker]
                    filter_ = (df.loc[sub,ticker]).tolist()
                    final = raw[filter_].tolist()
                    # print(final)
                    write_data(sub, ticker, final)
                    # set_html_page(sub, ticker, final)
                
            else: # received event is from ip
                #filter the subinfo
                data, topics, length = filter_msg_data(event)  # LIST OF TRUE/FALSE VALUES IN ORDER
                topics = numpy.array(topics)
                subscriber = data.get('username', None).lower()
                ticker = data.get('content', None).upper()
                #getusername = event[0] (subinfo)
                if not dict(list(df.index)).get(subscriber, False): # CHECKS IF THE SUBSCRIBER IS IN DF
                    addNewSubscriberToDf(df, subscriber)
                    if data.get('unsubscribe', False):
                        print(f"Un-subscribed to {ticker}")
                        unsubscribe(df, subscriber, ticker)
                    if not data.get('ads', False):
                        print("Unadvertise")
                        unadvertise(df, subscriber, ticker)

                    df.loc[subscriber, ticker, :] = topics
                    print(f"Updated df: {df}")
                    #df = addNewSubscriberToDf(df, username)
                    #update df like in phase 2
                else:
                    pass
                    #just update df
                    # not sure what to update here
    
    

def write_data(sub, ticker, data):
    copy = []
    with open("textfiles/" + sub + "_copy.txt", "w") as f:
        f.close()
    try:
        copyfile("textfiles/" + sub + "_data.txt", "textfiles/" + sub + "_copy.txt")
    except:
        pass
    with open("textfiles/" + sub + "_copy.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if ticker not in line:
                copy.append(line)
        # print(copy)
    with open("textfiles/" + sub + "_data.txt", "w") as f:
        for c in copy:
            f.write(c)
        f.write(ticker+",")
        for d in data:
            f.write(str(d)+",")
        f.write("\n")
        f.close()

def set_html_page(sub, ticker, data):
    file_dir = "templates/" + str(sub) + "_data.html"
    file_dir = "templates/test" + str(global_counter) + ".html"
    html = open("templates/home.html", "r").read()
    with open(file_dir, "w") as f:
        for d in data:
            index = html.index("{{element.content}}")
            html = html[:index] + str(d) + "</br>" + html[index:]
        html = html.replace("{{element.content}}", "")
        html = html.replace("{% for element in collection %}", "")
        html = html.replace("{% endfor %}", "")
        f.write(html)
    f.close()

def start():
    socket_server.listen()
    print("Server listening...")
    while True:
        socket_data, source = socket_server.accept() 
        thread = threading.Thread(target=handle_publisher_ip, args=(socket_data, source))
        thread.start()

def filter_msg_data(msg):
    data = {}
    r = []
    count = 0
    order = ['open','high','low','close','adjclose','volume','ads']
    msg_split = msg.split('&')
    for e in msg_split:
        key, value = e.split("=")
        if value == str(0):
            value = False
        if value == str(1):
            count += 1
            value = True
        data[key] = value
    for i in order:
        r.append(data.get(i, False))

    return data, r, count

if __name__ == '__main__':
    # THREAD FOR INFORMATION PROVIDER
    web_thread = threading.Thread(target=start)
    web_thread.start()

    # MAIN THREAD HOSTING CLIENT-SIDE
    print("Client-Handler online.")
    app = Flask(__name__)

    @app.route('/<string:subscriber>')
    def dynamic_subscribers(subscriber):
        # file_dir = str(subscriber) + "_data.html"
        # file_dir = "templates/test.html"
        file_dir = "textfiles/" + str(subscriber) + "_data.txt"

        if subscriber in subscribers:
            with open(file_dir, "r") as f:
                lines = f.readlines()
                collection = []
                for line in lines:
                    ticker_data = line.split(",")
                    for data in ticker_data:
                        collection.append(data)
            f.close()
            # print(ticker, collection)
            return render_template("home.html", collection=collection)
            # return send_from_directory("html","/templates/test.html")
            # return render_template(file_dir)
        else:
            return redirect("/")

    @app.route('/', methods=['POST', 'GET'])
    def home_page():
        if request.method == 'POST':
            subinfo = ""
            first = True
            for item in request.form:
                if first:
                    first = False
                    subinfo += str(item)+"="+str(request.form.get(item, 0))
                else:
                    subinfo += "&"+str(item)+"="+str(request.form.get(item, 0))

            data, topics, length = filter_msg_data(subinfo)  # LIST OF TRUE/FALSE VALUES IN ORDER
            topics = numpy.array(topics)
            subscriber = data.get('username', None).lower()
            ticker = data.get('content', None).upper()
            # print(topics)
            # print(subscriber)
            # print(ticker)
            # print(data)

            if (length >= 3 and subscriber != None and ticker != "") or (subscriber != "" and ticker != "" and data.get('unsubscribe', False)):
                if not dict(list(df.index)).get(subscriber, False):
                    print("Not in df")
                    rvlist = SN(subinfo)

                    if 'IP1' in rvlist:
                        addNewSubscriberToDf(df, subscriber)
                        if data.get('unsubscribe', False):
                            print(f"Un-subscribed to {ticker}")
                            unsubscribe(df, subscriber, ticker)
                        if not data.get('ads', False):
                            print("Unadvertise")
                            unadvertise(df, subscriber, ticker)

                        df.loc[subscriber, ticker, :] = topics
                        print(f"Updated df: {df}")
                        # pass  # use subscription info to update dataframe like you did in phase 2
                    elif 'IP2' in rvlist:
                        SendToIP2(subinfo)
                    elif 'IP3' in rvlist:
                        SendToIP3(subinfo)
                    # addNewSubscriberToDf(df, subscriber)

            return redirect('/' + str(subscriber))
        else:
            prompt = "Please enter subscription details:"
            return render_template('home.html', prompt=prompt)
    # app.run(host='localhost', port=8000)
    app.run(host="0.0.0.0", port=8000)



