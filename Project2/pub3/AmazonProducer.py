from kafka import KafkaProducer
import yfinance as yf
import pickle
import time
def advertise(event):
    event.loc['ad'] = "If you own at least 15 shares of our stock you will receive Amazon Prime for FREE!"
    return event
raw_event = yf.download(tickers='AMZN', period='1d', interval='1m').iloc[-1]
event = advertise(raw_event)
producer = KafkaProducer(bootstrap_servers='kafka-3:9094',value_serializer=pickle.dumps)
while True:
    producer.send('Amazon', value=event)
    time.sleep(5)
