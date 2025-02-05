from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from classoption import OptionChainData
import datetime


# create the app
app = Flask(__name__)
app.secret_key = 'secret key'
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nifty-option-data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create the extension
db = SQLAlchemy()

class Nifty(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.String)
    time = db.Column(db.String)
    call_max = db.Column(db.String)
    put_max = db.Column(db.String)
    result = db.Column(db.String)
    def __init__(self, date, time, call_max, put_max, result):
        self.date = date
        self.time = time
        self.call_max = call_max
        self.put_max = put_max
        self.result = result


# initialize the app with the extension
db.init_app(app)
with app.app_context():

    db.create_all()


@app.route('/')
def indexop():
    all_nifty = Nifty.query.all()
    return render_template('indexop.html',nifty = all_nifty)


@app.route('/insert')
def insert():

    OPTION = OptionChainData()
    OPTION.call_all_functions()
    date = str(datetime.datetime.now().date())
    time = str(datetime.datetime.now().time())
    put_max = str(OPTION.max_pain()[0])
    call_max = str(OPTION.max_pain()[1])
    result = str(OPTION.result)
    print(date, time,call_max, put_max)

    nifty = Nifty(date=date, time=time, call_max=call_max, put_max=put_max, result=result)
    db.session.add(nifty)
    db.session.commit()

    return redirect(url_for('indexop'))




if __name__ == '__main__':
    app.run(debug=True)
