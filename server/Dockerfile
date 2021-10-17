# Import base image for Python
FROM python:latest

# Import server files to image folder /server/
ADD InformationProvider.py /server/
ADD phase2.db /server/

# Base directory changed to /server/
WORKDIR /server/

COPY requirements.txt .

RUN pip3 install -r requirements.txt