import socket
import threading
# from app.IP2.InformationProvider2 import SendToIP1
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

# global_counter = 0

IP1_port = 5001
IP2_port = 5002
IP3_port = 5003

app_port = 8002 # --CHNG

format = 'utf-8'
header = 64
host_ip = socket.gethostbyname(socket.gethostname())
disconnect_msg = '!disconnnect'
# create socket
socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
location = (host_ip, IP1_port)
# bind socket
socket_server.bind(location)

db = sqlite3.connect('../phase2.db')
# subscriber_df.to_sql('subsciber',db,if_exists='replace',index=True,index_label='subs')
# filteredmsg_df.to_sql('filtered',db,if_exists='replace',index=True,index_label='subs')
columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Ads']
zeros = np.zeros((1, len(columns)))
# df = pd.DataFrame(zeros,index=[['initialize'],['MultiIndex']],columns = columns)
# df.index.names = ['sub ID','publisher']

df = pd.DataFrame(zeros, index=['initialize'], columns=columns)
df.index.names = ['sub ID']

df.loc[:, :] = False
df.loc[:, 'Ads'] = True

subscribers = []

# CHANGES TO BE MADE, FIND THIS COMMENT TO KNOW WHICH LINE TO CHANGE: --CHNG

# DICTIONARY TO HOLD WHICH IP HANDLES WHICH SUBSCRIBERS
handler_map = {}
# INITIALIZE handler map
handler_map['IP1'] = []
handler_map['IP2'] = []
handler_map['IP3'] = []


def SendToIP1(event):  # --CHNG
    # create socket
    socket_IP2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP1_location = (host_ip, IP1_port)
    socket_IP2_location = (host_ip, IP2_port)
    # bind socket
    socket_IP2.bind(socket_IP2_location)
    # connect publisher socket to IP1
    socket_IP2.connect(IP1_location)
    # serialize the pandas Series object into a string representation
    msg = pickle.dumps(event)
    # get length of string representation
    msg_length = len(msg)
    # convert message length to a string and encode it using utf-8
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    # send message length
    socket_IP2.send(send_length)
    # send message
    socket_IP2.send(msg)


def SendToIP3(event):  # --CHNG
    # create socket
    socket_IP2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    IP3_location = (host_ip, IP3_port)
    socket_IP2_location = (host_ip, IP2_port)
    # bind socket
    socket_IP2.bind(socket_IP2_location)
    # connect publisher socket to IP1
    socket_IP2.connect(IP3_location)
    # serialize the pandas Series object into a string representation
    msg = pickle.dumps(event)
    # get length of string representation
    msg_length = len(msg)
    # convert message length to a string and encode it using utf-8
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    # send message length
    socket_IP2.send(send_length)
    # send message
    socket_IP2.send(msg)


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
    df.loc[username, :] = False
    df.loc[username, 'Ads'] = True

    # df.loc[(username,'AAPL'),:] = False
    # df.loc[(username,'AAPL'),'Ads'] = True

    # df.loc[(username, 'LYFT'), :] = False
    # df.loc[(username, 'LYFT'), 'Ads'] = True
    #
    # df.loc[(username, 'AMZN'), :] = False
    # df.loc[(username, 'AMZN'), 'Ads'] = True

    # subscribers.append(username)

    return df


def unadvertise(df, subscriber):
    df.loc[subscriber, 'Ads'] = False
    # df.loc[(subscriber, ticker), 'Ads'] = False
    return df


def unsubscribe(df, subscriber):
    df.loc[subscriber, :] = False
    # df.loc[(subscriber, ticker), :] = False
    return df


tickers = ['LYFT']  # --CHNG
raw_msg_df = pd.DataFrame(columns=tickers)
filtered_msg_df = pd.DataFrame(columns=tickers)


def handle_publisher_ip(socket_data, source):
    # handles the individual connections between a client and a server
    print('[new connection] ip: %s  port: %s connected.' % (source[0], source[1]))
    while True:
        msg_length = socket_data.recv(header).decode(format)

        if msg_length:
            msg_length = int(msg_length)
            msg = socket_data.recv(msg_length)
            event = pickle.loads(msg)

            # IF THE MESSAGE RECEIVED IS THE FILTERED MESSAGE FROM ANOTHER CLIENT, WE NEED TO WRITE THIS DATA ONTO THIS DATABASE
            # THIS IS TO UPDATE EACH SUBSCRIBER'S INFO SO WE CAN PROPERLY NOTIFY EACH SUBSCRIBER THAT THIS IP HANDLES
            # THE WAY SUBSCRIBERS ARE NOTIFIED IS THAT EACH USER WILL HAVE THEIR OWN TXT FILE, THAT TXT FILE IS USED TO GENERATE A HTML PAGE AND RENDERED ON THE WEBSITE WITH THE UPDATED DATA FROM EACH PUBLISHER
            # WHAT WRITE_DATA DOES, IS IT TAKES A FILTERED MESSAGE AND STORES IT IN EACH SUBSCRIBER'S TXT FILE (WRITE_DATA TAKES SUBSCRIBER, TICKER, AND DATA IN FORM OF A LIST)
            if type(event) is type(pd.Series([])):
                if type(event.name) is type(()):
                    # TAKE THE FILTERED MESSAGE AND WRITE_DATA
                    # event is filtered msg
                    ticker, subscriber = event.name[0], event.name[1]

                    filtered_msg_df[ticker] = event

                    data = filtered_msg_df[ticker].tolist()

                    write_data(subscriber, ticker, data)
                    # need to notify subscriber of filtered msg
                    # filtered_msg_df[ticker] = event?

                # THIS ASSUMES THAT THE MESSAGE IS A PUBLISHER PUBLISH, WE NEED TO FILTER THE RAW DATA FROM THE YF API THROUGH THE DATAFRAME AND WRITE EACH FILTERED MESSAGE TO DATABASE
                # IF THE SUBSCRIBER IS HANDLED BY ANOTHER IP, THEN SEND TO THAT IP, THE FILTERED MESSAGE
                # WE NEED A WAY TO REMEMBER WHICH IP HANDLES WHICH SUBSCRIBERS

                # EVERYTIME A PUBLISHER PUBLISHES, WE NEED TO CHECK FOR ALL SUBS IN DF, IF THEY ARE IN SUBSCRIBERS (IF THEY ARE, THEN WRITE DATA TO THIS IP, IF NOT SEND THE FILTERED MESSAGE TO THE RIGHT IP)
                else:
                    ticker = event.name
                    # print(event)
                    raw_msg_df[ticker] = event
                    # print(raw_msg_df)
                    # addNewSubscriberToDf(df, 'jason')
                    # print(df)
                    # print(df.index.values)
                    print(f'df.index.values = {df.index.values}')
                    print(f'df.index.tolist() = {df.index.tolist()}')
                    # Append subscribers to list
                    for e in df.index.values:
                        if e not in subscribers:
                            subscribers.append(e)

                    print(f'IP1 DF: {df}\n')

                    for sub in df.index.tolist():
                        raw = (raw_msg_df[ticker].to_frame()).transpose().loc[ticker]
                        filter_ = (df.loc[sub].squeeze()).tolist()
                        final = raw[filter_].tolist()
                        print(f'Filtered data for {ticker} updating for {sub}')
                        if sub in subscribers:
                            write_data(sub, ticker, final)
                        elif sub in handler_map.get('IP1'):  # --CHNG
                            raw_msg = raw_msg_df[ticker]
                            filter_msg = raw_msg[df.loc[subscriber, :]]
                            filter_msg.name = (ticker, subscriber)
                            SendToIP1(filter_msg)  # --CHNG
                        elif sub in handler_map.get('IP3'):  # --CHNG
                            raw_msg = raw_msg_df[ticker]
                            filter_msg = raw_msg[df.loc[subscriber, :]]
                            filter_msg.name = (ticker, subscriber)
                            SendToIP3(filter_msg)  # --CHNG
                        else:
                            print(f'Something went wrong, sub {sub} is not handled by any IP')

                    # OLD METHOD, USED TO FILTER RAW PUBLISH DATA AND UPDATE EACH SUBSCRIBER TXT FILE HANDLED BY THIS IP ONLY
                    # for sub in subscribers:
                    #     raw = (raw_msg_df[ticker].to_frame()).transpose().loc[ticker]
                    #     filter_ = (df.loc[sub].squeeze()).tolist()
                    #     final = raw[filter_].tolist()
                    #     print(final)
                    #     write_data(sub, ticker, final)
                    #     # set_html_page(sub, ticker, final)

            # THE MESSAGE RECEIVED IS A QUERY MESSAGE (sub=john&ticker=aapl&topics=high+low+volume), USE THIS MESSAGE TO UPDATE DATAFRAME
            # WHERE THIS QUERY MESSAGE CAME FROM??? ADD A QUERY THAT REMEMBERS WHICH IP HANDLES WHICH SUBSCRIBER
            else:
                data, topics, length = filter_msg_data(event)  # LIST OF TRUE/FALSE VALUES IN ORDER
                topics = numpy.array(topics)
                subscriber = data.get('username', None).lower()
                ticker = data.get('content', None).upper()
                if subscriber not in df.index.tolist():  # CHECKS IF THE SUBSCRIBER IS IN DF
                    addNewSubscriberToDf(df, subscriber)
                if not data.get('ads', False):
                    print(f"{subscriber} unadvertised to {ticker}")
                    unadvertise(df, subscriber)
                if data.get('unsubscribe', False):
                    print(f"{subscriber} unsubscribed to {ticker}")
                    unsubscribe(df, subscriber)
                else:
                    df.loc[subscriber, :] = topics
                    print(f"Updated df: {df}")

                # Why do we need this? The message sent to this ip means that this ip is the right ip to handle this ticker
                # We don't need to send this to another ip (each ip will hold the dataframe for each sub that subbed to the corresponding ticker)
                # eg: Andrew subbed to aapl so ip1 will store Andrew in its dataframe
                # Everytime aapl publishes, Andrew's boolean series (in the dataframe) is used to filter the raw aapl publish, then this filtered message is sent to the right ip (that Andrew used to sub to aapl in this case maybe ip3)

                # MAP THE IP THAT HANDLES THE SUBSCRIBER FOR FUTURE PUBLISH TO WORK PROPERLY
                handler = data.get('handler', None)
                handler_map[handler].append(subscriber)

                # RAW_MSG_DF CONTAINS THE MOST RECENT YF PUBLISHED DATA (RAW) THIS NEEDS TO BE FILTERED AND SENT TO THE RIGHT IP
                raw_msg = raw_msg_df[ticker]
                filter_msg = raw_msg[df.loc[subscriber, :]]
                filter_msg.name = (ticker, subscriber)
                if handler == 'IP1':  # --CHNG
                    SendToIP1(filter_msg)  # --CHNG
                elif handler == 'IP3':  # --CHNG
                    SendToIP3(filter_msg)  # --CHNG
                else:
                    print("Some edge case was not checked or something is wrong with the message sending")


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
        f.write(ticker + ",")
        for d in data:
            f.write(str(d) + ",")
        f.write("\n")
        f.close()


# def set_html_page(sub, ticker, data):
#     file_dir = "templates/" + str(sub) + "_data.html"
#     file_dir = "templates/test" + str(global_counter) + ".html"
#     html = open("templates/home.html", "r").read()
#     with open(file_dir, "w") as f:
#         for d in data:
#             index = html.index("{{element.content}}")
#             html = html[:index] + str(d) + "</br>" + html[index:]
#         html = html.replace("{{element.content}}", "")
#         html = html.replace("{% for element in collection %}", "")
#         html = html.replace("{% endfor %}", "")
#         f.write(html)
#     f.close()

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
    order = ['open', 'high', 'low', 'close', 'adjclose', 'volume', 'ads']
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
                    subinfo += str(item) + "=" + str(request.form.get(item, 0))
                else:
                    subinfo += "&" + str(item) + "=" + str(request.form.get(item, 0))

            # IN THE QUERY MESSAGE, ALSO INCLUDE WHICH IP IT CAME FROM
            handler = "IP2"  # CHANGE THIS LINE TO THE CORRESPONDING IP HANDLER # --CHNG
            subinfo += "&handler=" + handler

            data, topics, length = filter_msg_data(subinfo)  # LIST OF TRUE/FALSE VALUES IN ORDER
            topics = numpy.array(topics)
            subscriber = data.get('username', None).lower()
            ticker = data.get('content', None).upper()

            if (length >= 3 and subscriber != None and ticker != "") or (
                    subscriber != "" and ticker != "" and data.get('unsubscribe', False)):
                rvlist = SN(subinfo)
                # CHECKS IF THE MSGDATA BEING SENT IS BEING HANDLED BY THIS IP, IF NOT SEND THE MSGDATA TO THE RIGHT IP
                if 'IP2' in rvlist:  # --CHNG
                    if subscriber not in df.index.tolist():
                        print(f'Subscriber {subscriber} is not in df, adding subscribe to df...')
                        addNewSubscriberToDf(df, subscriber)
                    if not data.get('ads', False):
                        print(f"{subscriber} unadvertised to {ticker}")
                        unadvertise(df, subscriber)
                    if data.get('unsubscribe', False):
                        print(f"{subscriber} unsubscribed to {ticker}")
                        unsubscribe(df, subscriber)
                    else:
                        df.loc[subscriber, :] = topics
                        print(f"Updated df: {df}")
                elif 'IP1' in rvlist:  # --CHNG
                    SendToIP1(subinfo)
                elif 'IP3' in rvlist:  # --CHNG
                    SendToIP3(subinfo)

            return redirect('/' + str(subscriber))
        else:
            prompt = "Please enter subscription details:"
            return render_template('home.html', prompt=prompt)


    # APP WILL RUN ON DIFFERENT PORTS
    # app.run(host='localhost', port=8000)
    app.run(host="0.0.0.0", port=app_port)


