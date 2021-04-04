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
                    db.cursor().execute("UPDATE USER SET PWD={cngPwd2} where id='admin'".format(cngPwd2))
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
        cur = db.cursor().execute('''SELECT B.DESCRIPT FROM NUMBER_CODE A
LEFT JOIN DESCRIPTION B ON B.COM_ID = A.COM_ID
WHERE A.CODE = {code}
ORDER BY A.COM_NUMBER, B.DESC_ID'''.format(code))
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
            db.cursor().execute('DELETE FROM NUMBER_CODE WHERE CODE = {code}'.format(code))
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
            cur = db.cursor().execute('SELECT COM_ID FROM COMPOSITION WHERE COM_NM = \'{compos}\''.formate(compos))
            rows = cur.fetchall()
            print(rows)
            if(len(rows) > 0):
                com_id = rows[0][0]

                db.cursor().execute('DELETE FROM DESCRIPTION WHERE COM_ID = {com_id}'.format(com_id))
                db.cursor().execute('DELETE FROM COMPOSITION WHERE COM_ID = {com_id}'.format(com_id))
                
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
        code = request.form['code']
        compos_list = []
        for i in range(1,11):
            try:
                compos_list.append(request.form['compos'+str(i)])
            except KeyError:
                compos_list.append(0)

        if code and not '' == code:
            for i, compos in enumerate(compos_list):
                if compos != '':
                    insertCode(code, i+1, compos)
    return redirect("/manager1")

def insertCode(code, comp_index, compos):
    db = connect_db()
    db.cursor().execute('insert or replace into NUMBER_CODE(CODE, COM_NUMBER, COM_ID) values({code},{comp_index},IFNULL((select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\'),0))'.format(code, comp_index, compos))
    db.commit()
    db.close()

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
                pass

        if compos and not '' == compos:
            comId = insertComposFunc(compos)
            for i, desc in enumerate(desc_list):
                if desc != '':
                    insertDescFunc(comId, i+1, desc)
        db.close()
    return redirect("/manager2")

def getComposId(compos):
    db = connect_db()
    cur = db.cursor().execute('select COM_ID FROM COMPOSITION WHERE COM_NM=\'{compos}\''.format(compos))
    id = cur.fetchall()[0]
    db.close()
    if id:
        return id
    else :
        return None

def insertComposFunc(compos):
    db = connect_db()
    id = getComposId(compos)
    if not id:
        cur = db.cursor().execute('select MAX(COM_ID) FROM COMPOSITION')
        row = cur.fetchall()
        row = row[0][0]
        if not row:
            row = 0

        row = row + 1
        db.cursor().execute('insert into COMPOSITION(COM_ID, COM_NM) values({row},\'{compos}\')'.format(row,compos))
    else :
        row = id[0]

    db.commit()
    db.close()
    return row

def insertDescFunc(comId, index, desc):
    db = connect_db()
    db.cursor().execute('insert or replace into DESCRIPTION(COM_ID, DESC_ID, DESCRIPT) values({comId},{index},\'{desc}\')'.format(comId,index,desc))
    db.commit()
    db.close()

@app.route("/checkCode", methods=['POST','GET'])
def checkCode(code):
    if not session.get("login"):
        return redirect("/login")
    print("checkCode")
    check = False
    if request.method == 'POST':
        check = checkCodeFunc(request.form['code'])
    return jsonify({'check' : check}), 200

def checkCodeFunc(code):
    check = False
    db = connect_db()
    cur = db.cursor().execute('select * from NUMBER_CODE where CODE = \'{code}\''.format(code))
    row = cur.fetchall()

    if len(row) != 0 :
        check = True
    db.close()
    return check

@app.route("/manager/upload",methods=['POST'])
def upload():
    if not session.get("login"):
        return redirect("/login")
    print("upload")
    if request.method == 'POST':
        f = request.files['file']
        if request.form['exampleRadios'] == 'option1':
            excelUpload(f, 1)
            return redirect("/manager1")
        else :
            excelUpload(f, 2)
            return redirect("/manager2")

    else :
        return redirect("/manager")
    
@app.route('/manager/downloadTemplate')
def downloadFile ():
    if not session.get("login"):
        return redirect("/login")
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "docs/Template.zip"
    return send_file(path, as_attachment=True)


def excelUpload(excelFile: FileStorage, option):
    #insert compos
    #insert code

    wb = load_workbook(filename=BytesIO(excelFile.read()))
    sheet = wb.get_sheet_by_name("데이터")

    if option == 1 and sheet[1][0].value == '코드':
        rowIndex = 2
        row = sheet[rowIndex]
        
        while row[0].value:
            code = row[0].value
            cellIndex = 1
            cellValue = row[cellIndex]
            while cellValue.value:
                insertCode(code, cellIndex, str(cellValue.value))
                cellIndex = cellIndex + 1
                try:
                    cellValue = row[cellIndex]
                except:
                    break
            rowIndex = rowIndex + 1
            row = sheet[rowIndex]


    elif option == 2 and sheet[1][0].value == '구분코드':
        rowIndex = 2
        row = sheet[rowIndex]
        
        while row[0].value:
            compId = insertComposFunc(row[0].value)
            cellIndex = 1
            cellValue = row[cellIndex]
            while cellValue.value:
                insertDescFunc(compId,cellIndex,str(cellValue.value))
                cellIndex = cellIndex + 1
                try:
                    cellValue = row[cellIndex]
                except:
                    break
            
            rowIndex = rowIndex + 1
            row = sheet[rowIndex]

    else :
        print("업로드 양식이 잘못되었습니다.")
        pass


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
