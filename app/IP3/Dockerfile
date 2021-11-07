FROM python:3.9.1
COPY . /IP3
WORKDIR /IP3
RUN pip install --upgrade pip
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5003
EXPOSE 5031
EXPOSE 5032
EXPOSE 8003
ENTRYPOINT ["python"]
CMD ["InformationProvider3.py"]