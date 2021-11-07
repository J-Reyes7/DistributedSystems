FROM python:3.9.1
COPY . /IP2
WORKDIR /IP2
RUN pip install --upgrade pip
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5002
EXPOSE 5021
EXPOSE 5023
EXPOSE 8002
ENTRYPOINT ["python"]
CMD ["InformationProvider2.py"]
