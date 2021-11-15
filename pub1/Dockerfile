FROM python:3.9.1
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
EXPOSE 5001
ENTRYPOINT ["python"]
CMD ["publisher1_Apple.py"]