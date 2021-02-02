from flask import Flask, g, render_template, request, redirect, jsonify
import sqlite3
from contextlib import closing
from src.data.CodeData import CodeData
from src.data.CompositionData import CompositionData
from log.Logger import Logger


app = Flask(__name__)



DATABASE = './rdbms/example.db'

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
    Logger.info("Entered manager1")
    cur = g.db.cursor().execute('SELECT A.CODE, A.COM_NUMBER, C.COM_NM FROM NUMBER_CODE A LEFT JOIN COMPOSITION C ON A.COM_ID = C.COM_ID ORDER BY A.CODE')
    rows = cur.fetchall()
    datas = []
    for r in rows:
        check = False

        for d in datas:
            if r[0] == d.code:
                check = True
                d.addComposition(r[1],r[2])
                break

        if not check:
            codeData = CodeData(r[0])
            codeData.addComposition(r[1],r[2])
            datas.append(codeData)
            
    result_data = []
    for d in datas:
        result_data.append(d.getSpreadData())

    cur = g.db.cursor().execute('SELECT COM_NM FROM COMPOSITION ORDER BY COM_ID')
    rows = cur.fetchall()
    rows = [r[0] for r in rows]

    return render_template("admin1.html", datas = datas, options=rows, layout=1)
     
@app.route("/manager2")
def manager2():
    Logger.info("Entered manager2")
    cur = g.db.cursor().execute('SELECT C.COM_NM, A.DESC_ID, A.DESCRIPT FROM DESCRIPTION A LEFT JOIN COMPOSITION C ON A.COM_ID = C.COM_ID ORDER BY C.COM_ID')
    rows = cur.fetchall()
    datas = []
    for r in rows:
        check = False

        for d in datas:
            if r[0] == d.composition:
                check = True
                d.addDescription(r[1],r[2])
                break

        if not check:
            composData = CompositionData(r[0])
            composData.addDescription(r[1],r[2])
            datas.append(composData)
            
    result_data = []
    for d in datas:
        result_data.append(d.getSpreadData())

    return render_template("admin2.html", datas = datas, layout=2)

@app.route("/result", methods=['POST'])
def result():
    Logger.info("Result Chat Page")
    if request.method == 'POST':
        code = -1
        code = request.form['code']
        cur = g.db.cursor().execute(f'''SELECT B.DESCRIPT FROM NUMBER_CODE A
LEFT JOIN DESCRIPTION B ON B.COM_ID = A.COM_ID
WHERE A.CODE = {code}
ORDER BY A.COM_NUMBER, B.DESC_ID''')
        rows = cur.fetchall()
        tempString=''
        if rows :
            tempString = '[{name: \'TEST_NAME\',avatar: null,messages: ['
            for i, row in enumerate(rows):
                if i != 0:
                    tempString = tempString + ','
                tempString = tempString + '{message: \'' + str(row[0]) + '\',sender: false}'

            tempString = tempString + ',{message: \'\',sender: false}]}];'
        
        return render_template("result.html", resultString=tempString, wrongway=False)
    else:
        rows = []
        return render_template("result.html", wrongway=True)

@app.route("/deleteCode", methods=['POST'])
def deleteCode():
    Logger.info("deleteCode")
    Logger.info(str(request.form))
    if request.method == 'POST':
        code = request.form['code']
        if code:
            g.db.cursor().execute(f'DELETE FROM NUMBER_CODE WHERE CODE = {code}')
            g.db.commit()

    return redirect("/manager1")

@app.route("/deleteDesc", methods=['POST'])
def deleteDesc():
    Logger.info("deleteDesc")
    Logger.info(str(request.form))
    if request.method == 'POST':
        code = request.form['code']
        if code:
            # g.db.cursor().execute(f'DELETE FROM NUMBER_CODE WHERE CODE = {code}')
            # g.db.commit()
            pass

    return redirect("/manager2")

@app.route("/insertCode", methods=['POST'])
def insertCode():
    Logger.info("insertCode")
    Logger.info(str(request.form))
    if request.method == 'POST':
        code = request.form['code']
        compos_list = []
        for i in range(1,11):
            try:
                compos_list.append(request.form['compos'+str(i)])
            except KeyError:
                Logger.info("[WARN] It Does not exists key")

        if code and not '' == code:
            for i, compos in enumerate(compos_list):
                if compos != '':
                    g.db.cursor().execute(f'insert or replace into NUMBER_CODE(CODE, COM_NUMBER, COM_ID) values({code},{i}+1,(select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\'))')
                    g.db.commit()

    return redirect("/manager1")

@app.route("/insertDesc", methods=['POST'])
def insertDesc():
    Logger.info("insertDesc")
    Logger.info(str(request.form))
    if request.method == 'POST':
        compos = request.form['compos']
        desc_list = []
        for i in range(1,11):
            try:
                desc_list.append(request.form['desc'+str(i)])
            except KeyError:
                Logger.info("[WARN] It Does not exists key")

        if compos and not '' == compos:
            for i, desc in enumerate(desc_list):
                if desc != '':
                    cur = g.db.cursor().execute(f'select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\'')
                    row = cur.fetchall()
                    if row:
                        row = row[0][0]
                        g.db.cursor().execute(f'insert or replace into DESCRIPTION(COM_ID, DESC_ID, DESCRIPT) values({row},{i}+1,\'{desc}\')')
                    else:
                        cur = g.db.cursor().execute(f'select MAX(COM_ID) FROM COMPOSITION')
                        row = cur.fetchall()
                        if row:
                            row = row[0][0]
                            g.db.cursor().execute(f'insert into COMPOSITION(COM_ID, COM_NM) values({row}+1,\'{compos}\')')
                            g.db.cursor().execute(f'insert or replace into DESCRIPTION(COM_ID, DESC_ID, DESCRIPT) values({row}+1,{i}+1,\'{desc}\')')
                        else:
                            g.db.cursor().execute(f'insert or replace into DESCRIPTION(COM_ID, DESC_ID, DESCRIPT) values(1,{i}+1,\'{desc}\')')
                            
                    g.db.commit()

    return redirect("/manager2")

@app.route("/checkCode", methods=['POST'])
def checkCode():
    Logger.info("checkCode")
    Logger.info(str(request.form))
    check = False
    if request.method == 'POST':
        code = request.form['code']
        cur = g.db.cursor().execute(f'select * from NUMBER_CODE where CODE = {code}')
        row = cur.fetchall()

        if len(row) != 0 :
            check = True

    return jsonify({'check' : check}), 200

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
    pass
    # url = 'http://localhost'
    #  webbrowser.open(url)
    # app.run(host='0.0.0.0', port=80, debug=True)
