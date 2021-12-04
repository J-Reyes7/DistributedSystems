from kafka import KafkaConsumer
import pickle
import threading
import pandas as pd
import time

raw_msg_df = pd.DataFrame(columns=['Apple','Lyft','Amazon'])
def handle_thread1():
    consumer1 = KafkaConsumer('Amazon',
                         group_id='group1',
                         bootstrap_servers='localhost:9094',
                         value_deserializer=pickle.loads)
    for message in consumer1:
        raw_msg_df['Amazon'] = message.value

thread1 = threading.Thread(target=handle_thread1)
thread1.start()

def handle_thread2():
    consumer2 = KafkaConsumer('Lyft',
                         group_id='group2',
                         bootstrap_servers='localhost:9093',
                         value_deserializer=pickle.loads)
    for message in consumer2:
        raw_msg_df['Lyft'] = message.value
        

thread2 = threading.Thread(target=handle_thread2)
thread2.start()

def handle_thread3():
    consumer3 = KafkaConsumer('Apple',
                         group_id='group3',
                         bootstrap_servers='localhost:9092',
                         value_deserializer=pickle.loads)
    for message in consumer3:
        raw_msg_df['Apple'] = message.value

thread3 = threading.Thread(target=handle_thread3)
thread3.start()

while True:
    print(raw_msg_df)
    time.sleep(5)