import socket
import threading
import yfinance as yf
import sqlite3
import numpy as np
import pandas as pd
import pickle
port = 5000
format = 'utf-8'
header = 64 
host_ip = socket.gethostbyname(socket.gethostname())
disconnect_msg = '!disconnnect'

socket_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
attach = (host_ip, port)
socket_server.bind(attach)


db = sqlite3.connect('phase2.db')

# subscriber_df.to_sql('subsciber',db,if_exists='replace',index=True,index_label='subs')
# filteredmsg_df.to_sql('filtered',db,if_exists='replace',index=True,index_label='subs')

# test = pd.read_sql_query('Select * from table;',db)
# test = test.set_index('subs')
columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
zeros = np.zeros((12,len(columns)))
df = pd.DataFrame(zeros,index=[['sub1','sub1','sub1','sub2','sub2','sub2','sub3','sub3','sub3','sub4','sub4','sub4'],['AAPL','LYFT','AMZN','AAPL','LYFT','AMZN','AAPL','LYFT','AMZN','AAPL','LYFT','AMZN']],columns = columns)
df.index.names = ['sub ID','publisher']
df.loc[:,:] = False

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
            ticker = event.name
            raw_msg_df[ticker] = event
            
            if msg == disconnect_msg:
                break
    
    socket_data.close()


def start():
    socket_server.listen() 
    while True:
        socket_data, source = socket_server.accept() 
        thread = threading.Thread(target=handle_publisher, args = (socket_data, source ))
        thread.start()

start()

