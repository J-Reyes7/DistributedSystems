FROM python:3.9.1
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["AppleProducer.py"]