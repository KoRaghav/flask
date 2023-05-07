from flask import Flask, render_template, request, url_for, flash, redirect, session, jsonify
from werkzeug.exceptions import abort
# import MySQLdb
from user import dis_user,editAboutme,list_of_user_date
from tag import get_tags,get_tags_list
from question import pagefunction2,pagefunction_number,question_from_list_of_tag_ml
from question import showQuestion_byscore_help,sort_que_by_time,sort_que_by_time_number,sort_quesbyTag,question_from_list_of_tag,question_from_list_of_tag_number
from particular_question import particular_que_from_id,answer_from_parent_id,score_question,put_answer,sort_ans_by_time
from particular_question import one_ans,check_score_count,check_score_count_answer,ask_question
from api import api
import json
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
from flask_cors import CORS

import re
app = Flask(__name__)
CORS(app)

def requestConnection():
    mydb = MySQLdb.connect(
        host='containers-us-west-162.railway.app',
    user='root',
    passwd='ufo2OWVGXtpgiPsXHUcW',
    db='askq',
    port=6118
    )
    return mydb

def requestCursor(conn):
    return conn.cursor()

app.config['SECRET_KEY'] = 'your secret key'



# ML API : Returns list of tags and 3 questions according to page number
@app.route('/ml/<int:page>/<string:query>',methods=['GET'])
def ml(query,page):
    l = api(query)
    m = question_from_list_of_tag_ml(l,page)
    return {'lst':[x[0] for x in l],'q':m}

# Get userdata by UserID
@app.route('/user/<int:id>',methods=['GET'])
def user_by_id(id):
    x = dis_user(id)  
    return(dict(enumerate(x)))

# Get list of users in a page
@app.route('/users/<int:page>',methods=['GET'])
def users_by_id(page):
    offset = 6*(page-1)
    x = list_of_user_date(page,True,False,False,False)
    return(dict(enumerate(x)))

# Get list of tags in a page
@app.route('/tag/<int:per_page>/<int:page>',methods=['GET'])
def tag_page(per_page,page):
    offset = 6*(page-1)
    pagination_users,total=get_tags(offset=offset,per_page=6)
    return dict(enumerate(pagination_users))

# Get total number of tags in DB
@app.route('/tag/number',methods=['GET'])
def tag_page_number():
    pagination_users,total=get_tags()
    return str(total)

# Get a list of all tags
@app.route('/tag/list',methods=['GET'])
def tag_list():
    l=[ {'value':x[0],'label':x[0]} for x in get_tags_list()]
    return dict(enumerate(l))
  


@app.route('/<string:tag>/<int:page>/time/question',methods=['GET'])
def display_question_score(tag,page): 
    ans=pagefunction2(page,tag=tag)
    return dict(enumerate(ans))


@app.route('/<string:tag>/<int:page>/score/question',methods=['GET'])
def display_question(tag,page): 
    ans=sort_quesbyTag(tag,page)
    return dict(enumerate(ans))

@app.route('/<string:tag>/question/number',methods=['GET'])
def display_question_number(tag): 
    ans=pagefunction_number(tag)
    return str(ans)


@app.route('/score/question/<int:page>',methods=['GET'])
def showQuestion_byscore(page):
    ans=showQuestion_byscore_help(page)
    return dict(enumerate(ans))

@app.route('/time/question/<int:page>',methods=['GET'])
def sort_que_by_time_main(page):
    ans=sort_que_by_time(page)
    return dict(enumerate(ans))

@app.route('/question/number',methods=['GET']) 
def sort_que_number():
    ans=sort_que_by_time_number()
    return str(ans)

@app.route('/<int:id>/answer',methods=['GET'])
def particular_question(id):
    l=particular_que_from_id(id)
    n=1
    return dict(enumerate(l))

@app.route('/<int:id>/answers',methods=['GET'])
def particular_question_answer(id):
    ans_list=answer_from_parent_id(id)
    m=len(ans_list)
    return dict(enumerate( ans_list))

@app.route('/ask/question', methods=['GET','POST']) 
def create():
    if 'loggedin' in session:
        if request.method == 'POST':
            title  = request.get_json()['Title']
            content = request.get_json()['Body']
            tag = request.get_json()['Tag'] 
            tag_list = [x["value"] for x in tag]
            ask_question(title,content,tag,tag_list)
            total =max_questionid()[0]
            return str(total)
           

def max_questionid():
    conn=requestConnection()
    cursor=requestCursor(conn)
    cursor.execute('SELECT @last_id := MAX(id) FROM Question')
    Current_questionid=cursor.fetchone()
    cursor.close()
    conn.close()
    return Current_questionid

@app.route('/login/', methods=['GET', 'POST'])
def login():
    msg = ''
    conn = requestConnection()
    cursor = requestCursor(conn)
    if request.method == 'POST':
        username = request.get_json()['Username']
        password = request.get_json()['Password']
        cursor.execute('SELECT * FROM User WHERE Display_Name = %s AND password = %s', (username, password,))
        account = cursor.fetchall()
        account = list(account)
        if account:
            session['loggedin'] = True
            session['username'] = account[0][1]
            session['id'] = account[0][0]
            print("logged")
            return "You "
        else:
            msg = 'Incorrect username/password!'
        cursor.close()
        conn.close()
    return msg

@app.route('/checkuser',methods=['GET'])
def checkuser():
    print("I am here")
    if "loggedin" in session:
        return "true"
    else:
        return "false"

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return "true"

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    conn = requestConnection()
    cursor = requestCursor(conn)
    if request.method=='POST':
        username = request.get_json()['Username']
        email = request.get_json()['Email']
        password = request.get_json()['Password']
        username1 = '"' + username + '"'
        cursor.execute('SELECT * FROM User WHERE Display_Name = ' +  (username1))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO User (Display_Name, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            msg = 'You have successfully registered!'
            return msg
    cursor.close()
    conn.close()
    return msg



@app.route('/user')
def show_user():
    if 'loggedin' in session:
      date,detail=dis_user(session['id'])
      return {"date":date,"detail":detail}
    else:
        msg = "Please login before"
        return "false"



@app.route('/<int:id>/upscore',methods=['PUT','GET'])
def up_score(id):
    if 'loggedin' in session:
        return (check_score_count(id,session['id'],1))
            

@app.route('/<int:id>/downscore',methods=['PUT','GET'])
def down_score(id):
    if 'loggedin' in session:
        return (check_score_count(id,session['id'],-1))

@app.route('/<int:id>/upans',methods=['PUT','GET'])
def up_ans(id):
    if 'loggedin' in session:
      return check_score_count_answer(id,session['id'],1)
    else:
        return "first logged in"

@app.route('/<int:id>/downans',methods=['PUT','GET'])
def down_ans(id):
    if 'loggedin' in session:
        return check_score_count_answer(id,session['id'],-1)
    else:
        return "first logged in"

@app.route('/<int:id>/new_ans',methods=['POST','GET'])
def newanswer(id):
    if 'loggedin' in session:
        if request.method == 'POST':
            content = request.get_json()['Answer']
            put_answer(id,session['id'],content)
        return "True"


@app.route('/user/aboutme',methods=['POST'])
def Update_About():
    body = request.get_json()['About']
    if 'loggedin' in session:
        id=session['id']
        editAboutme(id,body)
        return "True"
    else:
        return "first logged in"

@app.route('/<int:id>/score/ans',methods=['GET'])
def showAns_byscore(id):
    l,n,ans_list,m=sort_ans_by_time(id,0)
    return dict(enumerate(ans_list[::-1]))

@app.route('/<int:id>/time/ans',methods=['GET'])
def sort_ans_by_time_main(id):
    l,n,ans_list,m=sort_ans_by_time(id,1)
    return dict(enumerate(ans_list[::-1]))


@app.route('/')
def index():
    print("5")
    return render_template('index.html')

if __name__=="__main__":
    app.run(port=5000)