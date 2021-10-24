FROM python:3.9.1
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
#RUN pip3 install flask
#RUN pip3 install flask-sqlalchemy
#RUN export FLASK_APP=app.py
EXPOSE 5000
EXPOSE 5002
ENTRYPOINT ["python"]
CMD ["publisher2_Lyft.py"]