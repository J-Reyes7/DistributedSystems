import socket
import threading
import yfinance as yf
import sqlite3
import numpy as np
import pandas as pd
import re

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
def publish(tickers):
  return yf.download(tickers=tickers, period='1d', interval='1m')
# raw_msg = publish()
# if raw_msg.shape[0] ==0:
#     #invalid stock symbol
#     pass
# else:
#     #valid
#     pass

def df_to_sql(info):
    info.to_sql('table',db,if_exists='append',index=True,index_label='subs')
    print(pd.read_sql_table('table',db))
    pass

def handle_subscriber(socket_data, source):
    # handles the individual connections between a client and a server
    print('[new connection] ip: %s  port: %s connected.' % (source[0],source[1]))
    subscriber = source[1]-5000
    while True:
        msg_length = socket_data.recv(header).decode(format)
        if msg_length: 
            msg_length = int(msg_length)
            msg = socket_data.recv(msg_length).decode(format)
            if msg == disconnect_msg:
                break
            print('received message from port %i: %s' % (source[1], msg))
            filter_ = re.findall(r'\$[A-Za-z]+', msg)
            if len(filter_) == 0:
                print(f"Invalid ticker {msg}")
                socket_data.send(f"Subscriber #{subscriber} requested an invalid ticker. Please type $ followed by a ticker; $ABC\n".encode(format))
            else:
                socket_data.send(f"Subscriber #{subscriber} processing your request...".encode(format))
                ticker = filter_[0].replace("$", "")
                ticker_data = publish(ticker)
                if ticker_data.empty:
                    print(f"Invalid ticker {msg}")
                    socket_data.send(f"Subscriber #{subscriber} requested an invalid ticker. Please type $ followed by a ticker; $ABC\n".encode(format))
                else:
                    socket_data.send(f"Subscriber #{subscriber} request processed!\n".encode(format))
                    print(ticker_data)
                    # df_to_sql(ticker_data)

                # DO STUFF HERE WITH RETRIEVED DATA (ticker_data)



                # val = 'Hi subscriber %i, your msg was received.' % subscriber
                # socket_data.send(val.encode(format))
    
    socket_data.close()


def start():
    socket_server.listen() 
    while True:
        socket_data, source = socket_server.accept() 
        thread = threading.Thread(target=handle_subscriber, args = (socket_data, source ))
        thread.start()

start()