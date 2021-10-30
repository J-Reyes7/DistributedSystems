FROM python:3.9.1
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
EXPOSE 8000
ENTRYPOINT ["python"]
CMD ["InformationProvider.py"]