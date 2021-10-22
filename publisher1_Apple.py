import socket
import yfinance as yf 
import pickle
import time

port = 5000
format = 'utf-8'

header = 64  
host_ip = socket.gethostbyname(socket.gethostname())
disconnect_msg = '!disconnnect'
socket_sub1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
attach = (host_ip, port)

socket_sub1.bind((host_ip,5001))
socket_sub1.connect(attach)  

def publish(event):
    # message = msg.encode(format)
    msg = pickle.dumps(event)
    msg_length = len(msg)
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    socket_sub1.send(send_length)
    socket_sub1.send(msg)

while True:

    event = yf.download(tickers='AAPL', period='1d', interval='1m').iloc[-1]
    event.name = 'AAPL'
    publish(event)
    time.sleep(10)
    


