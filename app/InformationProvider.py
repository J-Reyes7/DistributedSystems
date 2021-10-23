import socket
import threading
import yfinance as yf
import sqlite3
import numpy as np
import pandas as pd
import pickle
import numpy
from flask import Flask, render_template, request, redirect, url_for

port = 5000
format = 'utf-8'
header = 64 
host_ip = socket.gethostbyname(socket.gethostname())
disconnect_msg = '!disconnnect'

socket_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
attach = (host_ip, port)
socket_server.bind(attach)


db = sqlite3.connect('../phase2.db')

# subscriber_df.to_sql('subsciber',db,if_exists='replace',index=True,index_label='subs')
# filteredmsg_df.to_sql('filtered',db,if_exists='replace',index=True,index_label='subs')

# test = pd.read_sql_query('Select * from table;',db)
# test = test.set_index('subs')
columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Ads']
zeros = np.zeros((12,len(columns)))
df = pd.DataFrame(zeros,index=[['sub1','sub1','sub1','sub2','sub2','sub2','sub3','sub3','sub3','sub4','sub4','sub4'],['AAPL','LYFT','AMZN','AAPL','LYFT','AMZN','AAPL','LYFT','AMZN','AAPL','LYFT','AMZN']],columns = columns)
df.index.names = ['sub ID','publisher']
df.loc[:,:] = False

df.loc[:,'Ads'] = True
def unadvertise(df, subscriber,ticker):
    df.loc[(subscriber, ticker),'Ads'] = False
    return df

def insert_db():
    pass

tickers = ['AAPL','LYFT','AMZN']
raw_msg_df = pd.DataFrame(columns = tickers)

filtered_msg_df = pd.DataFrame(columns = tickers)
def handle_publisher(socket_data, source):
    # handles the individual connections between a client and a server
    print('[new connection] ip: %s  port: %s connected.' % (source[0],source[1]))
    while True:
        #msg_length = socket_data.recv(header)
        msg_length = socket_data.recv(header).decode(format)
        
        if msg_length: 
            msg_length = int(msg_length)
            msg = socket_data.recv(msg_length)
            event = pickle.loads(msg)
            print(event)
            ticker = event.name
            raw_msg_df[ticker] = event

            if msg == disconnect_msg:
                break
    
    socket_data.close()


def start():
    socket_server.listen()
    print("Server listening...")
    while True:
        socket_data, source = socket_server.accept() 
        thread = threading.Thread(target=handle_publisher, args = (socket_data, source ))
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

    @app.route('/sub')
    def dynamic_subscribers(subscriber):
        # Make a
        return render_template(str(subscriber) + "_data.html")

    @app.route('/', methods=['POST', 'GET'])
    def home_page():
        if request.method == 'POST':
            send_msg = ""
            first = True
            for item in request.form:
                if first:
                    first = False
                    send_msg += str(item)+"="+str(request.form.get(item, 0))
                else:
                    send_msg += "&"+str(item)+"="+str(request.form.get(item, 0))

            # THIS IS THE MSG WE WANT TO USE TO UPDATE SUB/UNSUB
            # print(send_msg)

            data, topics, length = filter_msg_data(send_msg)  # LIST OF TRUE/FALSE VALUES IN ORDER
            if length >= 3:
                topics = numpy.array(topics)
                subscriber = data.get('username', 'None').lower()
                ticker = data.get('content', 'None').upper()
                if data.get('ads', False):
                    unadvertise(df, subscriber, ticker)
                print(topics)
                print(subscriber)
                print(ticker)
                df.loc[subscriber, ticker] = topics
                print(df)


            return redirect('/')
        else:
            prompt = "Please enter comany's stock symbol"
            return render_template('home.html', prompt=prompt)
            # return render_template('home.html', prompt=prompt, collection=collection)
    app.run(host='localhost', port=8000)
    # app.run(host="0.0.0.0",port=8000)



