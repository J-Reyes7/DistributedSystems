How to deploy:
1) Build image from Dockerfile
2) Use this image to create a container which hosts the website for clients to use. Since the Dockerfile exposes port 5000 and 8000, please specify the ports using the following format (desired host port number):5000, same for 8000.
3) Use docker build -t <image_name> . to create the docker image
4) Use docker container run --publish <port:port> -d(detached can be emitted) <image_name> to run the container
5) Now that the broker container is running, you can use the website to send messages to the broker for sub/unsub with topics included.
6) Make sure the publishers also are dockerized using the same method from 1 to 4

Description of design: 
We used Flask to deploy the client part of the project. This allows multiple clients to sub and unsub to the broker.
The broker takes a query string from the clients response in Flask and filters the request to the username and topics
from the specified ticker. The information is then put into a textfile for that specific user and the information provider
uses the textfile to generate personal webpages to render to each user.