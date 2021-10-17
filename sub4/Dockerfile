# Import base image for Python
FROM python:latest

# Import client files to image folder /client/
ADD subscriber4.py /client/

# Base directory changed to /client/
WORKDIR /client/

COPY requirements.txt .

RUN pip3 install -r requirements.txt