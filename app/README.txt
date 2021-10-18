How to deploy:
1) Build image frome Dockerfile
2) Use this image to create a container using interactive mode. Since the Dockerfile exposes port 5000, please specify the ports using the following format (desired host port number):5000. 
3) Once inside the container use the following to initialize the database:
    - python3
    - from app import db
    - db.create_all()
4) Use exit() to exit python's interactive mode 
5) With the database now initialized, use flask run --host=0.0.0.0 to start the server


Description of design: 
I used flask for my web framework and sqlite3 for my database. When the client submits 
a GET request the server uses the else block of the home_page function to collect any
database entries. An updated HTML page is then rendered and served to the client. The 
server handles a POST request in the if block of the home_page function. A 'symbols' 
object is first created using the data the client provided and subsequently added to 
the database. A GET request is then submitted and an updated HTML page is generated 
and served to the client. 
