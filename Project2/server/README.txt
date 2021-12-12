How to deploy:
1) Make sure /data folder is not in the /kafka folder before deploying
2) To deply, simply navigate to the Project2/Kafka folder and run docker-compose up --build -d

Description of design: 
We used Flask to deploy the client part of the project. This allows multiple clients to sub and unsub to the broker.
The broker takes a query string from the clients response in Flask and filters the request to the username and topics
from the specified ticker. The information is then put into a textfile for that specific user and the information provider
uses the textfile to generate personal webpages to render to each user.

For Kafka, we chose to use python-kafka for our producers and consumers. We have a total of 3 broker nodes in Kafka when run and 10 premade subscribers as well as 3 topics.
We used a premade Kafka image for our docker and referenced it from: https://github.com/jay3393/docker-development-youtube-series/tree/master/messaging/kafka

Our publishers again get new information from the yfinance API in realtime and with our producer objects, we send the information to the kafka brokers. 
Then on our server app, we have our consumers that consume these messages from the kafka brokers and update our database so that we can notify the subscribers.

The data is filtered the same way using series of boolean values and dataframes of the live data from the API.
Nothing was changed about the web application except small changes that had to be made due to the change in structure from personal brokers to kafka brokers.