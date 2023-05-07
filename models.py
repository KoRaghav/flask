from flask import Flask, render_template, request, url_for, flash, redirect, session
from werkzeug.exceptions import abort
from flask_paginate import Pagination, get_page_args
import MySQLdb
from user import dis_user,editDisplayname,editAboutme,list_of_user_date
from tag import get_tags,get_tags_list
from question import pagefunction,pagefunction2,pagefunction_number,pagefunction_number_all
from question import showQuestion_byscore_help,sort_que_by_time,sort_que_by_time_number,sort_quesbyTag,question_from_list_of_tag,question_from_list_of_tag_number
# from particular_question import particular_que_from_id,answer_from_parent_id
from particular_question import particular_que_from_id,answer_from_parent_id,score_question,put_answer,sort_ans_by_time
from particular_question import one_ans
from api import api
import json


# from user import check_login
# from flask_socketio import SocketIO
app = Flask(__name__)
# socketio=SocketIO(app)

def requestConnection():
    mydb = MySQLdb.connect(host='localhost',
    user='root',
    passwd='root',
    db='askq')
    return mydb

def requestCursor(conn):
    return conn.cursor()
app.config['SECRET_KEY'] = 'your secret key'


@app.route('/user/<int:id>',methods=['GET'])
def user_by_id(id):
    x = dis_user(id)
    # print(x)
    return(dict(enumerate(x)))

@app.route('/users/<int:page>',methods=['GET'])
def users_by_id(page):
    offset = 6*(page-1)
    x = list_of_user_date(page,True,False,False,False)
    return(dict(enumerate(x)))

@app.route('/tag/<int:per_page>/<int:page>',methods=['GET'])
def tag_page(per_page,page):
    offset = 6*(page-1)
    pagination_users,total=get_tags(offset=offset,per_page=6)
    return dict(enumerate(pagination_users))

@app.route('/ml/<string:query>',methods=['GET'])
def ml(query):
    l = api(query)
    return dict(enumerate(l))
    # return ""

@app.route('/tag/number',methods=['GET'])
def tag_page_number():
    pagination_users,total=get_tags()
    return str(total)

@app.route('/tag/list',methods=['GET'])
def tag_list():
    l=[ {'value':x[0],'label':x[0]} for x in get_tags_list()]
    # print(l)
    return dict(enumerate(l))

@app.route('/search/<int:page>/<string:query>',methods=['POST'])
def search(page,query):
    taglist  = request.get_json()['Taglist']
    if taglist == {} : return {}
    l= question_from_list_of_tag(list(taglist.values()),page)
    return dict(enumerate(l))    

@app.route('/search/number/<string:query>',methods=['POST'])
def search_number(query):
    taglist  = request.get_json()['Taglist']
    l= question_from_list_of_tag_number(list(taglist.values()))
    return str(l)   


@app.route('/<string:tag>/<int:page>/time/question',methods=['GET'])
def display_question_score(tag,page): # took care when question is less than 3
    ans=pagefunction2(page,tag=tag)
    # print(ans)
    return dict(enumerate(ans))


@app.route('/<string:tag>/<int:page>/score/question',methods=['GET'])
def display_question(tag,page): # took care when question is less than 3
    ans=sort_quesbyTag(tag,page)
    # print(ans)
    return dict(enumerate(ans))


@app.route('/<string:tag>/question/number',methods=['GET'])
def display_question_number(tag): # took care when question is less than 3
    ans=pagefunction_number(tag=tag)
    return str(ans)

# @app.route('/question/number',methods=['GET'])
# def display_question_number_all(): # took care when question is less than 3
#     ans=pagefunction_number_all()
#     return str(ans)

@app.route('/question')
def zaurez():
    ans=pagefunction("flex")
    # print(ans[0])
    return dict(enumerate( ans))
   



@app.route('/')
def index():
    tag='flex'
    return render_template('index.html',tag=tag)

# @app.route('/answer',methods=['POST'])
# def after_posting_question():
#     return render_template('particular_question.html')

@app.route('/score/question/<int:page>',methods=['GET'])
def showQuestion_byscore(page):
    ans=showQuestion_byscore_help(page)
    return dict(enumerate(ans))

@app.route('/time/question/<int:page>',methods=['GET'])
def sort_que_by_time_main(page):
    ans=sort_que_by_time(page)
    return dict(enumerate(ans))

@app.route('/question/number',methods=['GET']) # what does this api doing
def sort_que_number():
    ans=sort_que_by_time_number()
    print('number...........................',ans)
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

@app.route('/ask/question', methods=['GET','POST']) #error in this function as id not generated in good ways
def create():
    if 'loggedin' in session:
        # print(session['id'])

        if request.method == 'POST':
            # if check_login: # how he checked here login by zaurez
            title  = request.get_json()['Title']
            content = request.get_json()['Body']
            tag = request.get_json()['Tag'] # take care of how to get particular tag from list of tags
            tag_list = [x["value"] for x in tag]
            # tag = "" # take care of how to get particular tag from list of tags
            # tag_list=tag.split()
            conn = requestConnection()
            cursor = requestCursor(conn)
            # print(title,content,session['id'])
            # cursor.execute('INSERT INTO Question (Title, Body,Owner_User_Id,Score) VALUES ("%s","%s", "%s","%s")',(title, content,session['id'],0))
            cursor.execute('INSERT INTO Question (Title, Body,Score) VALUES ("%s","%s","%s")',(title, content,0))
            conn.commit()
            total =max_questionid()[0]
            print(total)
            for k in tag_list:
               cursor.execute('INSERT INTO Tag (ID,tags) VALUES ("%s", "%s")',(total,k))
               conn.commit()
            cursor.close()
            conn.close()
            print("total..............",total)
            return str(total)
            # return redirect(url_for('after_posting_question',id=total))
    # else:
    #     return redirect(url_for('login'))
    # return render_template('new_question.html')

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
        # password=check_password_hash(user.password, password) #working but need to increase password size
        # username = '"' + username + '"'
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
# Remember to remove duplicacy from account
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        # elif not re.match(r'[A-Za-z0-9]+', username):
        #     msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
        # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO User (Display_Name, password) VALUES (%s, %s)', (username, password))
            conn.commit()
            msg = 'You have successfully registered!'
            # return redirect(url_for('show_user'))
            return msg
    cursor.close()
    conn.close()
    return msg
    # return render_template('signup.html', msg=msg)



@app.route('/user')
def show_user():
    if 'loggedin' in session:
      print("test..............")
      date,detail=dis_user(session['id'])
      print(detail[9],"hkj")
      return {"date":date,"detail":detail}
    else:
        # print('hi')
        msg = "Please login before"
        return "false"



@app.route('/<int:id>/upscore',methods=['PUT','GET'])
def up_score(id):
    print("..............",id)
    # start editing
    sql1 = "SELECT JSON_EXTRACT(my_list, '$') AS list FROM help where id = " + str(id)
    l=cursor.execute(sql1)
    l=cursor.fetchall()
    l =(l[0][0])
    my_list = json.loads(l, parse_int=int) # this list my_list guves the list of id of all user who have voted it up or down
    loged_in_user_id = session['id']
    if loged_in_user_id in my_list:
        command = "You can Vote only once"
    else:
        # ALlow to upvote or downvote
        my_list.append(loged_in_user_id)
        sql2 = "INSERT INTO help (id, my_list)VALUES (%s, %s)"
        cursor.execute(sql2,(2,json.dumps(my_list),))

    mydb.commit()
    cursor.close()
    #end editing
    if 'loggedin' in session:
        l=score_question(1,id)
        return str(l)
    # else:
    #     return redirect(url_for('login'))

@app.route('/<int:id>/downscore',methods=['PUT','GET'])
def down_score(id):
    if 'loggedin' in session:
        l=score_question(-1,id) 
        return str(l)
    # else:
    #     return redirect(url_for('login'))    

@app.route('/<int:id>/upans',methods=['PUT','GET'])
def up_ans(id):
    if 'loggedin' in session:
      print("satyam")
      return str(one_ans(1,id))
    else:
        print("hello")
        return "first logged in"

@app.route('/<int:id>/downans',methods=['PUT','GET'])
def down_ans(id):
    if 'loggedin' in session:
      return str(one_ans(-1,id))

@app.route('/<int:id>/new_ans',methods=['POST','GET'])
def newanswer(id):
    if 'loggedin' in session:
        if request.method == 'POST':
            content = request.get_json()['Answer']
            # print("test...", content)
            # content = request.form['Answer']
            put_answer(id,session['id'],content)
            #put_answer(id,session['id'],content)
            # return redirect(url_for('particular_question',id=id))
        return "True"
    # else:
    #     return redirect(url_for('login'))

@app.route('/user/displayname')
def Update_name(name):
    if 'loggedin' in session:
        id=session['id']
        editDisplayname(id,name)
        return "True"
    else:
        return "first logged in"

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


if __name__=="__main__":
    app.run(host='0.0.0.0',debug=True,port=3014)