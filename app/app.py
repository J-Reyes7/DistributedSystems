from flask import Flask, render_template, request,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocksymbol.db'
db = SQLAlchemy(app)

class symbols(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(5), nullable = False)

    def __repr__(self):
        return '<Symbol %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def home_page():
    if request.method == 'POST':

        csymbol = request.form['content']
        new_csymbol = symbols(content=csymbol)

        
        db.session.add(new_csymbol)
        db.session.commit()
        return redirect('/')  
    else:
        prompt = "Please enter comany's stock symbol"
        collection = symbols.query.order_by(symbols.content).all()
        return render_template('home.html', prompt = prompt, collection = collection)

        if __name__ == '__main__':
            app.run(host="0.0.0.0",port=5001)

