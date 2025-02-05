from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3
from classoption import OptionChainData
import datetime


db = sqlite3.connect("niftyy.db")
cursor = db.cursor()
#cursor.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, time varchar(250) NOT NULL UNIQUE, call_max varchar(250) NOT NULL, put_max varchar(250) NOT NULL, result varchar(250) NOT NULL)")

OPTION = OptionChainData()
OPTION.call_all_functions()
time = str(datetime.datetime.now().time())
put_max = str(OPTION.max_pain()[1])
call_max = str(OPTION.max_pain()[0])
result = str(OPTION.result)



cursor.execute(f"INSERT INTO books VALUES(1, '{time}', '{call_max}', '{put_max}','{result}')")
db.commit()

@app.route('/')
def indexop():
    all_nifty = Nifty.query.all()


    return render_template('indexop.html',nifty = all_nifty)

