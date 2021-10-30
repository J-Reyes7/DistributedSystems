import socket
import yfinance as yf 
import pickle
import time

port = 5003
format = 'utf-8'

header = 64  
host_ip = socket.gethostbyname(socket.gethostname())
# create socket
socket_pub3 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
IP3_location = (host_ip, port)
socket_pub3_location = (host_ip,4003)
# bind socket
socket_pub3.bind(socket_pub3_location)
# connect publisher socket to IP3
socket_pub3.connect(IP3_location) 

def publish(event):
    # serialize the pandas Series object into a string representation
    msg = pickle.dumps(event)
    # get length of string representation
    msg_length = len(msg)
    # convert message length to a string and encode it using utf-8
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    # send message length 
    socket_pub3.send(send_length)
    # send message 
    socket_pub3.send(msg)
# adds an advertisement to Series object
def advertise(event):
    event.loc['ad'] = "If you own at least 15 shares of our stock you will receive Amazon Prime for FREE!"
    return event
while True:
    # pull stock data from yahoo finance API
    raw_event = yf.download(tickers='AMZN', period='1d', interval='1m').iloc[-1]
    raw_event.name = 'AMZN'
    event = advertise(raw_event)
    publish(event)
    time.sleep(10)
    