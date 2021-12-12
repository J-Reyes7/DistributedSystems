from kafka import KafkaProducer
import yfinance as yf
import pickle
import time
def advertise(event):
    event.loc['ad'] = "If you own at least 5 shares you will receive 40% off Lyft Pink!"
    return event
raw_event = yf.download(tickers='LYFT', period='1d', interval='1m').iloc[-1]
event = advertise(raw_event)
producer = KafkaProducer(bootstrap_servers='kafka-2:9093',value_serializer=pickle.dumps)
while True:
    producer.send('Lyft', value=event)
    time.sleep(5)