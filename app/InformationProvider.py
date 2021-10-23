import socket
import threading
import yfinance as yf
import sqlite3
import numpy as np
import pandas as pd
import pickle
from flask import Flask, render_template, request, redirect, url_for

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

def handle_publisher(socket_data, source):
    # handles the individual connections between a client and a server
    print('[new connection] ip: %s  port: %s connected.' % (source[0],source[1]))
    while True:
        #msg_length = socket_data.recv(header)
        msg_length = socket_data.recv(header).decode(format)
        print(msg_length)
        
        if msg_length: 
            msg_length = int(msg_length)
            msg = socket_data.recv(msg_length)
            print(msg)
            event = pickle.loads(msg)
            
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





def app():
    print("Client-Handler online.")
    app = Flask(__name__)

    app.run(host='localhost', port=8000)

    @app.route('/', methods=['POST', 'GET'])
    def home_page():
        if request.method == 'POST':

            csymbol = request.form['content']

            return redirect('/')
        else:
            prompt = "Please enter comany's stock symbol"
            return render_template('home.html', prompt=prompt)
            # return render_template('home.html', prompt=prompt, collection=collection)
    # app.run(host="0.0.0.0",port=8000)

if __name__ == '__main__':
    web_thread = threading.Thread(target=app)
    web_thread.start()
    start()

