FROM python:3.9.1
COPY . /server
WORKDIR /server
RUN pip install --upgrade pip
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 8000
EXPOSE 9092
EXPOSE 9093
EXPOSE 9094
ENTRYPOINT ["python"]
CMD ["Subscribers.py"]