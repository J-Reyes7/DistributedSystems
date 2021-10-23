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

socket_sub1.bind((host_ip,5002))
socket_sub1.connect(attach)  

def publish(event):
    # message = msg.encode(format)
    msg = pickle.dumps(event)
    msg_length = len(msg)
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    socket_sub1.send(send_length)
    socket_sub1.send(msg)

def advertise(event):
    event.loc['ad'] = "If you own at least 5 shares you will receive 40% off Lyft Pink!"
    return event
while True:

    raw_event = yf.download(tickers='LYFT', period='1d', interval='1m').iloc[-1]
    raw_event.name = 'LYFT'
    event = advertise(raw_event)
    publish(event)
    time.sleep(10)
