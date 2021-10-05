import socket
import threading
import yfinance as yf
import sqlite3
import numpy as np
import pandas as pd

port = 5000
format = 'utf-8'
header = 64 
host_ip = socket.gethostbyname(socket.gethostname())
disconnect_msg = '!disconnnect'

socket_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
attach = (host_ip, port)
socket_server.bind(attach)


db = sqlite3.connect('phase2.db')

initial = np.zeros((4,5))
columns = ['max','min','current','raw','filtered']
index = ['sub1','sub2','sub3','sub4']
df = pd.DataFrame(initial,index=index,columns=columns)

# df.to_sql('table',db,if_exists='replace',index=True,index_label='subs')
# test = pd.read_sql_query('Select * from table;',db)
# test = test.set_index('subs')
# def publish():
#   return yf.download(tickers='AAPL', period='1d', interval='1m')
# raw_msg = publish()
# if raw_msg.shape[0] ==0:
#     #invalid stock symbol
#     pass
# else:
#     #valid 
#     pass

def handle_subscriber(socket_data, source):
    # handles the individual connections between a client and a server
    print('[new connection] ip: %s  port: %s connected.' % (source[0],source[1]))
    while True:
        msg_length = socket_data.recv(header).decode(format) 
        if msg_length: 
            msg_length = int(msg_length)
            msg = socket_data.recv(msg_length).decode(format)
            if msg == disconnect_msg:
                break
            print('received message from port %i: %s' % (source[1],msg))
            val = 'Hi subscriber %i, your msg was received.' % (source[1]-5000)
            socket_data.send(val.encode(format))
    
    socket_data.close()


def start():
    socket_server.listen() 
    while True:
        socket_data, source = socket_server.accept() 
        thread = threading.Thread(target=handle_subscriber, args = (socket_data, source ))
        thread.start()

start()