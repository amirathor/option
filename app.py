from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

# create the app
app = Flask(__name__)
app.secret_key = 'secret key'
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create the extension
db = SQLAlchemy()

class Books(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    rating = db.Column(db.String, nullable=False)
    def __init__(self, title, author, rating):
        self.title = title
        self.author = author
        self.rating = rating


# initialize the app with the extension
db.init_app(app)
with app.app_context():
    db.create_all()
@app.route('/')
def Index():
    all_books = Books.query.all()

    return render_template('index.html',books = all_books)



@app.route('/insert', methods = ['POST'])
def insert():

    if request.method == 'POST':

        title = request.form['title']
        author = request.form['author']
        rating = request.form['rating']

        book = Books(title, author, rating)
        db.session.add(book)
        db.session.commit()
        flash("Book Added Successfully")
        return redirect(url_for('Index'))

@app.route('/update', methods = ['GET','POST'])
def update():

     if request.method == 'POST':
         book = Books.query.get(request.form.get('id'))

         book.title = request.form['title']
         book.author = request.form['author']
         book.rating = request.form['rating']

         db.session.commit()
         flash("Book Updated Successfully")
         return redirect(url_for('Index'))

@app.route('/delete/<id>/', methods = ['GET','POST'])
def delete(id):

    book = Books.query.get(id)
    db.session.delete(book)
    db.session.commit()
    flash("Book Deleted Successfully")
    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(debug=True)