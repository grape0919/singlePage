from flask import Flask, g, render_template
import sqlite3
from contextlib import closing

app = Flask(__name__)

DATABASE = 'rdbms/example.db'

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/")
def root():
    return render_template("example.html")

@app.route("/manager1")
def manager1():
    cur = g.db.cursor().execute('SELECT COM_ID, TITLE, QUESTION FROM QUESTION WHERE Q_ID = {ID}'.format(ID=id))
    return render_template("admin1.html")
     
@app.route("/manager2")
def manager2():
    return render_template("admin2.html")

@app.route("/result")
def result():
    return render_template("result.html")

def connect_db():
    return sqlite3.connect(DATABASE)

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('rdbms/0.DROP_TABLES.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()
        with app.open_resource('rdbms/1.CREATE_TABLES.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()


if __name__ == '__main__':
     
     url = 'http://localhost'
    #  webbrowser.open(url)
     app.run(host='0.0.0.0', port=80, debug=True)