import socket


port = 5000
format = 'utf-8'

header = 64 
host_ip = socket.gethostbyname(socket.gethostname())
disconnect_msg = '!disconnnect'
socket_sub1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
attach = (host_ip, port)

socket_sub1.bind((host_ip,5004))
socket_sub1.connect(attach)  

def send(msg):
    message = msg.encode(format)
    msg_length = len(message)
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    socket_sub1.send(send_length)
    socket_sub1.send(message)

while True:
    send(input('Enter stock ticker ($):'))
    processing = True
    while processing:
        res = socket_sub1.recv(1024).decode(format)
        print(res)
        if "processing" not in res:
            processing = False
        # print(socket_sub1.recv(3000).decode(format))

