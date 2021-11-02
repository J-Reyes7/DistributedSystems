FROM python:3.9.1
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5003
ENTRYPOINT ["python"]
CMD ["publisher3_Amazon.py"]