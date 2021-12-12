from kafka import KafkaConsumer
import pickle
import threading
import pandas as pd
import time

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

app_port = 8000

# <----------------------------------------CONSUMER THREADS---------------------------------------->
raw_msg_df = pd.DataFrame(columns=['AAPL','LYFT','AMZN']) # raw_msg_df to use to filter with our database df

def handle_thread1():
    print("Started consumer1")
    consumer1 = KafkaConsumer('Amazon',
                         group_id='group1',
                         bootstrap_servers='kafka-3:9094',
                         value_deserializer=pickle.loads)
    for message in consumer1:
        # print("consumer1{}".format(message))
        raw_msg_df['AMZN'] = message.value


thread1 = threading.Thread(target=handle_thread1)
thread1.start()

def handle_thread2():
    print("Started consumer2")
    consumer2 = KafkaConsumer('Lyft',
                         group_id='group2',
                         bootstrap_servers='kafka-2:9093',
                         value_deserializer=pickle.loads)
    for message in consumer2:
        # print("consumer2{}".format(message))
        raw_msg_df['LYFT'] = message.value


thread2 = threading.Thread(target=handle_thread2)
thread2.start()

def handle_thread3():
    print("Started consumer3")
    consumer3 = KafkaConsumer('Apple',
                         group_id='group3',
                         bootstrap_servers='kafka-1:9092',
                         value_deserializer=pickle.loads)
    for message in consumer3:
        # print("consumer3{}".format(message))
        raw_msg_df['AAPL'] = message.value

thread3 = threading.Thread(target=handle_thread3)
thread3.start()





# <----------------------------------------Dataframe Initialization---------------------------------------->
columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Ads']
zeros = np.zeros((30,len(columns)))
df = pd.DataFrame(zeros,index=[[
    'sub1','sub1','sub1',
    'sub2','sub2','sub2',
    'sub3','sub3','sub3',
    'sub4','sub4','sub4',
    'sub5','sub5','sub5',
    'sub6','sub6','sub6',
    'sub7','sub7','sub7',
    'sub8','sub8','sub8',
    'sub9','sub9','sub9',
    'sub10','sub10','sub10'
    ],[
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN',
    'AAPL','LYFT','AMZN'
    ]],columns = columns)
df.index.names = ['sub','pub']
df.loc[:,:] = False
df.loc[:,'Ads'] = True





# <----------------------------------------Subscriber Methods---------------------------------------->
subscribers = []

def addNewSubscriberToDf(df, username):
    df.loc[(username,'AAPL'),:] = False
    df.loc[(username,'AAPL'),'Ads'] = True

    df.loc[(username, 'LYFT'), :] = False
    df.loc[(username, 'LYFT'), 'Ads'] = True

    df.loc[(username, 'AMZN'), :] = False
    df.loc[(username, 'AMZN'), 'Ads'] = True

    return df
addNewSubscriberToDf(df, 'John')
df.loc[('John','AAPL'),:] = True
def unadvertise(df, subscriber, ticker):
    df.loc[(subscriber, ticker),'Ads'] = False
    return df

def unsubscribe(df, subscriber, ticker):
    df.loc[(subscriber, ticker), :] = False
    return df





# <----------------------------------------Updates---------------------------------------->
def update():
    while True:

        try:
            for sub in dict(df.index.tolist()):
                aapl_topics = (df.loc[sub, 'AAPL']).tolist()
                lyft_topics = (df.loc[sub, 'LYFT']).tolist()
                amzn_topics = (df.loc[sub, 'AMZN']).tolist()
                # print(aapl_topics)
                # print(raw_msg_df['AAPL'])
                raw_aapl = (raw_msg_df['AAPL'].to_frame()).transpose().loc['AAPL']
                raw_lyft = (raw_msg_df['LYFT'].to_frame()).transpose().loc['LYFT']
                raw_amzn = (raw_msg_df['AMZN'].to_frame()).transpose().loc['AMZN']
                print(raw_aapl)
                filter_aapl = raw_aapl[aapl_topics].tolist()
                filter_lyft = raw_lyft[lyft_topics].tolist()
                filter_amzn = raw_amzn[amzn_topics].tolist()

                # raw = (raw_msg_df[ticker].to_frame()).transpose().loc[ticker]
                # filter_ = (df.loc[sub].squeeze()).tolist()
                # final = raw[filter_].tolist()
                print(f'Updating for {sub}')
                print(filter_aapl)
                # print(raw_msg_df)
                if sub in subscribers:
                    write_data(sub, 'AAPL', filter_aapl)
                    write_data(sub, 'LYFT', filter_lyft)
                    write_data(sub, 'AMZN', filter_amzn)
        except Exception as e:
            print(f'ERROR: {e}')
            print(f'Empty raw_msg_df: {raw_msg_df}')
            pass
        time.sleep(5)





def write_data(sub, ticker, data):
    print(data)
    print(f'Updating {sub}...')
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
    web_thread = threading.Thread(target=update)
    web_thread.start()

    # MAIN THREAD HOSTING CLIENT-SIDE
    print("Client-Handler online.")
    app = Flask(__name__)

    @app.route('/<string:subscriber>')
    def dynamic_subscribers(subscriber):
        file_dir = "textfiles/" + str(subscriber) + "_data.txt"
        try:
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
        except:
            pass
        # else:
        return redirect("/")

    """Event handler for when the client visits the homepage"""
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

            if (length >= 3 and subscriber != None and ticker != "") or (subscriber != "" and ticker != "" and data.get('unsubscribe', False)):
                    subscribers.append(subscriber)
                    if not dict(list(df.index)).get(subscriber, False):
                        print(f'Subscriber {subscriber} is not in df, adding subscribe to df...')
                        addNewSubscriberToDf(df, subscriber)
                    if not data.get('ads', False):
                        print(f"{subscriber} unadvertised to {ticker}")
                        unadvertise(df, subscriber, ticker)
                    if data.get('unsubscribe', False):
                        print(f"{subscriber} unsubscribed to {ticker}")
                        unsubscribe(df, subscriber, ticker)
                    else:
                        df.loc[subscriber, ticker, :] = topics
                        print(f"Updated df: {df}")

            return redirect('/' + str(subscriber))
        else:
            prompt = "Please enter subscription details:"
            return render_template('home.html', prompt=prompt)

    # APP WILL RUN ON DIFFERENT PORTS
    # app.run(host='localhost', port=8000)
    app.run(host="0.0.0.0", port=app_port)