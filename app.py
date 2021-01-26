from flask import Flask, g, render_template, request, redirect
import sqlite3
from contextlib import closing
from src.data.CodeData import CodeData
from src.data.CompositionData import CompositionData
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
    return render_template("index.html")

@app.route("/manager1")
def manager1(): #숫자코드 - 구분 등록/삭제
    cur = g.db.cursor().execute('SELECT A.CODE, A.COM_NUMBER, C.COM_NM FROM NUMBER_CODE A LEFT JOIN COMPOSITION C ON A.COM_ID = C.COM_ID')
    rows = cur.fetchall()
    datas = []
    for r in rows:
        check = False

        for d in datas:
            if r[0] == d.code:
                check = True
                print('r1 : ', r[1])
                print('r2 : ', r[2])
                d.addComposition(r[1],r[2])
                break

        if not check:
            print("new codeData")
            codeData = CodeData(r[0])
            print(codeData.code)
            print(codeData.composition_list)
            codeData.addComposition(r[1],r[2])
            datas.append(codeData)
            
    result_data = []
    for d in datas:
        result_data.append(d.getSpreadData())

    print(result_data)
    cur = g.db.cursor().execute('SELECT COM_NM FROM COMPOSITION ORDER BY COM_ID')
    rows = cur.fetchall()
    rows = [r[0] for r in rows]

    return render_template("admin1.html", datas = datas, options=rows)
     
@app.route("/manager2")
def manager2():
    cur = g.db.cursor().execute('SELECT C.COM_NM, A.DESC_ID, A.DESCRIPT FROM DESCRIPTION A LEFT JOIN COMPOSITION C ON A.COM_ID = C.COM_ID ORDER BY C.COM_ID')
    rows = cur.fetchall()
    datas = []
    for r in rows:
        check = False

        for d in datas:
            if r[0] == d.composition:
                check = True
                print('r1 : ', r[1])
                print('r2 : ', r[2])
                d.addDescription(r[1],r[2])
                break

        if not check:
            composData = CompositionData(r[0])
            print(composData.composition)
            print(composData.description_list)
            composData.addDescription(r[1],r[2])
            datas.append(composData)
            
    result_data = []
    for d in datas:
        result_data.append(d.getSpreadData())

    print(result_data)

    return render_template("admin2.html", datas = datas)

@app.route("/result", methods=['POST'])
def result():
    if request.method == 'POST':
        #temp = request.form['num']
        code = -1
        code = request.form['code']
        print( "code =", code)
        cur = g.db.cursor().execute(f'SELECT CODE, COM_NUMBER, COM_ID FROM NUMBER_CODE WHERE CODE = {code}')
        rows = cur.fetchall()
        for row in rows:
            cur = g.db.cursor().execute(f'SELECT COM_NM FROM COMPOSITION WHERE CODE = {code}')
    else:
        rows = []
    return render_template("result.html", datas=rows)

@app.route("/deleteCode", methods=['POST'])
def deleteCode():
    print("deleteCode")
    if request.method == 'POST':
        code = request.form['code']
        if code:
            g.db.cursor().execute(f'DELETE FROM NUMBER_CODE WHERE CODE = {code}')
            g.db.commit()

    return redirect("/manager1")

@app.route("/deleteDesc", methods=['POST'])
def deleteDesc():
    print("deleteDesc")
    if request.method == 'POST':
        code = request.form['code']
        if code:
            # g.db.cursor().execute(f'DELETE FROM NUMBER_CODE WHERE CODE = {code}')
            # g.db.commit()
            pass

    return redirect("/manager2")

@app.route("/insertCode", methods=['POST'])
def insertCode():
    print("insertCode")
    if request.method == 'POST':
        print(request.form)
        code = request.form['code']
        compos_list = []
        for i in range(10):
            try:
                compos_list.append(request.form['compos'+str(i)])
            except KeyError:
                print("[WARN] It Does not exists key")

        if code and not '' == code:
            for i, compos in enumerate(compos_list):
                if compos != '':
                    g.db.cursor().execute(f'insert or replace into NUMBER_CODE(CODE, COM_NUMBER, COM_ID) values({code},{i}+1,(select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\'))')
                    g.db.commit()

    return redirect("/manager1")

@app.route("/insertDesc", methods=['POST'])
def insertDesc():
    print("insertDesc")
    if request.method == 'POST':
        print(request.form)
        compos = request.form['compos']
        compos_list = []
        for i in range(10):
            try:
                compos_list.append(request.form['compos'+str(i)])
            except KeyError:
                print("[WARN] It Does not exists key")

        if code and not '' == code:
            for i, compos in enumerate(compos_list):
                if compos != '':
                    # g.db.cursor().execute(f'insert or replace into NUMBER_CODE(CODE, COM_NUMBER, COM_ID) values({code},{i}+1,(select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\'))')
                    # g.db.commit()
                    pass

    return redirect("/manager2")

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