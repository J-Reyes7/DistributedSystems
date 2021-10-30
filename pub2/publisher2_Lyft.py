import socket
import yfinance as yf 
import pickle
import time

port = 5002
format = 'utf-8'

header = 64  
host_ip = socket.gethostbyname(socket.gethostname())
# create socket
socket_pub2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
IP2_location = (host_ip, port)
socket_pub2_location = (host_ip,4002)
# bind socket
socket_pub2.bind(socket_pub2_location)
# connect publisher socket to IP2
socket_pub2.connect(IP2_location) 

def publish(event):
    # serialize the pandas Series object into a string representation
    msg = pickle.dumps(event)
    # get length of string representation
    msg_length = len(msg)
    # convert message length to a string and encode it using utf-8
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    # send message length 
    socket_pub2.send(send_length)
    # send message
    socket_pub2.send(msg)
# adds an advertisement to Series object
def advertise(event):
    event.loc['ad'] = "If you own at least 5 shares you will receive 40% off Lyft Pink!"
    return event
while True:
    # pull stock data from yahoo finance API
    raw_event = yf.download(tickers='LYFT', period='1d', interval='1m').iloc[-1]
    raw_event.name = 'LYFT'
    event = advertise(raw_event)
    publish(event)
    time.sleep(10)
