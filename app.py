from flask import Flask, g, render_template, request, redirect, jsonify, session, flash, send_file
import sqlite3
from contextlib import closing
from flask.globals import current_app

from flask.signals import template_rendered
from src.data.CodeData import CodeData
from src.data.CompositionData import CompositionData
# from log.Logger import Logger
import os

from io import BytesIO
from openpyxl import load_workbook

from werkzeug.datastructures import FileStorage

app = Flask(__name__)


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

DATABASE = os.path.join(PROJECT_ROOT,'rdbms','example.db')
def connect_db():
    return sqlite3.connect(DATABASE)
#@app.before_request
#def before_request():

#@app.teardown_request
#def teardown_request(exception):
#    if db != None:
#        db.close()

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/login")
def login():
    if session.get("login"):
        session.pop("login")
        return redirect("/login")
    return render_template("login.html")

@app.route("/loginCheck", methods=["POST"])
def loginCheck():
    if session.get("login"):
        return redirect("/manager")
    if request.method == 'POST':
        db = connect_db()
        # user = request.form['user']
        password = request.form['password']
        print(password)
        cur = db.cursor().execute("SELECT PWD from USER where id='admin'")
        rows = cur.fetchall()
        print(rows)
        
        db.close()
        if 1 == len(rows):
            pwd = rows[0][0]
            if pwd == password:
                print("로그인 성공")
                
                ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                print("ip = ", ip)
                session["login"] = ip
                return redirect("manager1")
            else:
                flash("로그인 실패")
                return render_template("alertPage.html", redirect="/login")
        else:
            flash("로그인 실패")
            return render_template("alertPage.html", redirect="/login")


@app.route("/logout")
def logout():
    if session.get("login"):
        session.pop("login")
        flash("관리자 로그아웃 되었습니다.")
        return render_template("alertPage.html", redirect="/login")
    else:
        return redirect("/login")

@app.route("/cngAdmPwd", methods=['POST'])
def cngAdmPwd():
    if not session.get("login"):
        return redirect("/login")
    
    if request.method == 'POST':
        print(request.form)
        curPwd = request.form['curPwd']
        cngPwd1 = request.form['cngPwd1']
        cngPwd2 = request.form['cngPwd2']
        if len(cngPwd1) < 4 or len(cngPwd2) < 4:
            flash("비밀번호는 4자리 이상이어야 합니다.")
            return render_template("alertPage.html", redirect="/manager3")
            
        db = connect_db()
        cur = db.cursor().execute("SELECT PWD from USER where id='admin'")
        rows = cur.fetchall()
        if 1 == len(rows):
            pwd = rows[0][0]
            if pwd == curPwd:
                if cngPwd1 == cngPwd2:
                    db.cursor().execute(f"UPDATE USER SET PWD={cngPwd2} where id='admin'")
                    db.commit()
                    db.close()
                    flash("정상적으로 변경되었습니다. 다시 로그인해 주세요.")
                    return render_template("alertPage.html", redirect="/login")
                else:
                    print("변경 비번 달라")
                    db.close()
                    flash("바꿀 비밀번호/확인이 다릅니다.")
                    return render_template("alertPage.html", redirect="/manager3")
            else:
                print("현재 비번 달라")
                db.close()
                flash("현재 비밀번호가 틀렸습니다.")
                return render_template("alertPage.html", redirect="/manager3")
    else:
        return redirect("/login")

@app.route("/manager")
def manager():
    return redirect("/manager1")

@app.route("/manager1")
def manager1(): #숫자코드 - 구분 등록/삭제
    if not session.get("login"):
        return redirect("/login")
    db = connect_db()
    print("Entered manager1")
    cur = db.cursor().execute('SELECT A.CODE, A.COM_NUMBER, C.COM_NM FROM NUMBER_CODE A LEFT JOIN COMPOSITION C ON A.COM_ID = C.COM_ID ORDER BY A.CODE')
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

    cur = db.cursor().execute('SELECT COM_NM FROM COMPOSITION ORDER BY COM_ID')
    rows = cur.fetchall()
    rows = [r[0] for r in rows]
    db.close()
    return render_template("admin1.html", datas = datas, options=rows, layout=1)
     
@app.route("/manager2")
def manager2():
    if not session.get("login"):
        return redirect("/login")

    print("Entered manager2")
    db = connect_db()
    cur = db.cursor().execute('SELECT C.COM_NM, A.DESC_ID, A.DESCRIPT FROM DESCRIPTION A LEFT JOIN COMPOSITION C ON A.COM_ID = C.COM_ID ORDER BY C.COM_ID')
    rows = cur.fetchall()
    db.close()
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

@app.route("/manager3")
def manager3():
    if not session.get("login"):
        return redirect("/login")
    return render_template("admin3.html", layout=3)

@app.route("/result", methods=['POST'])
def result():
    if not session.get("login"):
        return redirect("/login")

    print("Result Chat Page")
    if request.method == 'POST':     
        db = connect_db()
        code = -1
        code = request.form['code']
        cur = db.cursor().execute(f'''SELECT B.DESCRIPT FROM NUMBER_CODE A
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
        db.close()
        return render_template("result.html", resultString=tempString, wrongway=False)
    else:
        rows = []
        return render_template("result.html", wrongway=True)

@app.route("/deleteCode", methods=['POST'])
def deleteCode():
    if not session.get("login"):
        return redirect("/login")
    print("deleteCode")
    print(str(request.form))
    if request.method == 'POST':  
        db = connect_db()
        code = request.form['code']
        if code:
            db.cursor().execute(f'DELETE FROM NUMBER_CODE WHERE CODE = {code}')
            db.commit()
        db.close()
    return redirect("/manager1")

@app.route("/deleteDesc", methods=['POST'])
def deleteDesc():
    if not session.get("login"):
        return redirect("/login")
    print("deleteDesc")
    print(str(request.form))
    if request.method == 'POST':
        db = connect_db()
        compos = request.form['compos']
        if compos:
            cur = db.cursor().execute(f'SELECT COM_ID FROM COMPOSITION WHERE COM_NM = \'{compos}\'')
            rows = cur.fetchall()
            print(rows)
            if(len(rows) > 0):
                com_id = rows[0][0]

                db.cursor().execute(f'DELETE FROM DESCRIPTION WHERE COM_ID = {com_id}')
                db.cursor().execute(f'DELETE FROM COMPOSITION WHERE COM_ID = {com_id}')
                
                db.commit()
            pass
        db.close()
    return redirect("/manager2")

@app.route("/insertCode", methods=['POST'])
def insertCode():
    if not session.get("login"):
        return redirect("/login")
    print("insertCode")
    print(str(request.form))
    if request.method == 'POST':  
        db = connect_db()
        code = request.form['code']
        compos_list = []
        for i in range(1,11):
            try:
                compos_list.append(request.form['compos'+str(i)])
            except KeyError:
                print("[WARN] It Does not exists key")

        if code and not '' == code:
            for i, compos in enumerate(compos_list):
                if compos != '':
                    db.cursor().execute(f'insert or replace into NUMBER_CODE(CODE, COM_NUMBER, COM_ID) values({code},{i}+1,(select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\'))')
                    db.commit()
        db.close()
    return redirect("/manager1")

@app.route("/insertDesc", methods=['POST'])
def insertDesc():
    if not session.get("login"):
        return redirect("/login")
    print("insertDesc")
    print(str(request.form))
    if request.method == 'POST':
        db = connect_db()
        compos = request.form['compos']
        desc_list = []
        for i in range(1,11):
            try:
                desc_list.append(request.form['desc'+str(i)])
            except KeyError:
                print("[WARN] It Does not exists key")

        if compos and not '' == compos:
            for i, desc in enumerate(desc_list):
                if desc != '':
                    cur = db.cursor().execute(f'select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\'')
                    row = cur.fetchall()
                    if row:
                        row = row[0][0]
                        db.cursor().execute(f'insert or replace into DESCRIPTION(COM_ID, DESC_ID, DESCRIPT) values({row},{i}+1,\'{desc}\')')
                    else:
                        cur = db.cursor().execute(f'select MAX(COM_ID) FROM COMPOSITION')
                        row = cur.fetchall()
                        if row:
                            row = row[0][0]
                            db.cursor().execute(f'insert into COMPOSITION(COM_ID, COM_NM) values({row}+1,\'{compos}\')')
                            db.cursor().execute(f'insert or replace into DESCRIPTION(COM_ID, DESC_ID, DESCRIPT) values({row}+1,{i}+1,\'{desc}\')')
                        else:
                            db.cursor().execute(f'insert or replace into DESCRIPTION(COM_ID, DESC_ID, DESCRIPT) values(1,{i}+1,\'{desc}\')')
                            
                    db.commit()
        db.close()
    return redirect("/manager2")

@app.route("/checkCode", methods=['POST'])
def checkCode():
    if not session.get("login"):
        return redirect("/login")
    print("checkCode")
    print(str(request.form))
    check = False
    if request.method == 'POST':
        db = connect_db()
        code = request.form['code']
        cur = db.cursor().execute(f'select * from NUMBER_CODE where CODE = {code}')
        row = cur.fetchall()

        if len(row) != 0 :
            check = True
        db.close()
    return jsonify({'check' : check}), 200

@app.route("/manager/upload",methods=['POST'])
def upload():
    if not session.get("login"):
        return redirect("/login")
    print("upload")
    print(request.form)
    if request.method == 'POST':
        db = connect_db()
        f = request.files['file']
        excelUpload(f)
        db.close()

    if request.form['exampleRadios'] == 'option1':
        return redirect("/manager1")
    else :
        return redirect("/manager2")

@app.route('/manager/downloadTemplate')
def downloadFile ():
    if not session.get("login"):
        return redirect("/login")
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "docs/Template.zip"
    return send_file(path, as_attachment=True)


def excelUpload(excelFile: FileStorage):
    print(type(excelFile))
    #excelFile.filename
    wb = load_workbook(filename=BytesIO(excelFile.read()))
    print(wb.get_sheet_by_name("데이터"))

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('rdbms/0.DROP_TABLES.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()
        with app.open_resource('rdbms/1.CREATE_TABLES.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()


if __name__ == '__main__':
    # pass
    # url = 'http://localhost'
    #  webbrowser.open(url)
    app.secret_key = 'hkdevstudio'
    #app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=80, debug=True)
