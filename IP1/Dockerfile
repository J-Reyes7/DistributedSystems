FROM python:3.9.1
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5001
EXPOSE 5012
EXPOSE 5013
EXPOSE 8001
ENTRYPOINT ["python"]
CMD ["InformationProvider1.py"]