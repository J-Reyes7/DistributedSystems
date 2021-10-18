FROM python:3.9.1
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip3 install flask 
RUN pip3 install flask-sqlalchemy
RUN export FLASK_APP=app.py
EXPOSE 5000
ENTRYPOINT ["/bin/sh"]

