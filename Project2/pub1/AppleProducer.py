from kafka import KafkaProducer
import yfinance as yf
import pickle
import time
def advertise(event):
    event.loc['ad'] = "If you own at least 5 shares you will receive a 50% off the new Macbook Pro!"
    return event
raw_event = yf.download(tickers='AAPL', period='1d', interval='1m').iloc[-1]
event = advertise(raw_event)
producer = KafkaProducer(bootstrap_servers='kafka-1:9092',value_serializer=pickle.dumps)
while True:
    producer.send('Apple', value=event)
    time.sleep(5)