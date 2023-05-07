
import MySQLdb
import json

def requestConnection():
    mydb = MySQLdb.connect(host='localhost',
    user='root',
    passwd='root',
    db='askq')
    return mydb

def requestCursor(conn):
    return conn.cursor()


def particular_que_from_id(id):
    conn=requestConnection()
    cursor=requestCursor(conn)
    a=cursor.execute('select * from Question where ID='+str(id))
    a=cursor.fetchall()
    b=cursor.execute('select tags from Tag where ID='+str(id))
    b=cursor.fetchall()
    a=list(a)
    a.append(list(b))
    cursor.close()
    conn.close()
    return a


def answer_from_parent_id(id):
    conn = requestConnection()
    cursor = requestCursor(conn)
    l = cursor.execute('SELECT * FROM Answer where Parent_ID = ' + str(id))
    l = cursor.fetchall()
    Answer_list = []
    for k in range(len(l)):
        Answer_list.append(l[k])
    return Answer_list

def score_question(Up,id):
        conn = requestConnection()
        cursor = requestCursor(conn)
        cursor.execute('select Score from Question where id='+str(id))
        score=cursor.fetchone()
        cursor.execute('Update Question set Score= '+str(score[0]+Up)+' where Id='+str(id))
        Ownerid=cursor.execute('select Owner_User_Id,Score from Question where Id= '+str(id))
        Ownerid=cursor.fetchone()
        ownscore=Ownerid[1]
        Ownerid=Ownerid[0]
        if Up==1:
          cursor.execute('Update User set up_votes='+str(ownscore+Up)+' where id='+str(Ownerid))
        else:
            cursor.execute('Update User set down_votes='+str(ownscore+Up)+' where id='+str(Ownerid))
        conn.commit()
        cursor.close()
        conn.close()
        l=particular_que_from_id(id)
        return l[0][3]


def sort_ans_by_time(id,time):
    conn = requestConnection()
    cursor = requestCursor(conn)
    l=particular_que_from_id(id)
    n=1
    if time:
      ans_list= cursor.execute('SELECT * FROM Answer  where Parent_ID = ' + str(id)+' Order by Creation_Date')
    else:
        ans_list= cursor.execute('SELECT * FROM Answer  where Parent_ID = ' + str(id)+' Order by Score')
    ans_list = cursor.fetchall()
    Answer_list = []
    m=len(ans_list)
    for k in range(m):
        Answer_list.append(ans_list[k])
    cursor.close()
    conn.close()
    return l,n,Answer_list,m 

def put_answer(id,ownerid,body):
    if body!="":
        conn = requestConnection()
        cursor = requestCursor(conn)
        cursor.execute('insert into Answer (Owner_User_Id,Parent_ID,Score,Body) Values ("%s","%s","%s","%s")',(ownerid,id,0,body))
        conn.commit()
        cursor.close()
        conn.close()
        return ""
    else:
        return ""


def one_ans(Up,id):
        conn = requestConnection()
        cursor = requestCursor(conn)
        cursor.execute('select Score from Answer where id='+str(id))
        score=cursor.fetchone()
        cursor.execute('Update Answer set Score= '+str(score[0]+Up)+' where Id='+str(id))
        Ownerid=cursor.execute('select Owner_User_Id,Score from Answer where Id= '+str(id))
        Ownerid=cursor.fetchone()
        ownscore=Ownerid[1]
        Ownerid=Ownerid[0]
        if Up==1:
          cursor.execute('Update User set up_votes='+str(ownscore+Up)+' where id='+str(Ownerid))
        else:
            cursor.execute('Update User set down_votes='+str(ownscore+Up)+' where id='+str(Ownerid))
        conn.commit()
        cursor.close()
        conn.close()
        return score[0]+Up


def check_score_count(id,userid,up):
        conn = requestConnection()
        cursor = requestCursor(conn)
        l = cursor.execute("SELECT JSON_EXTRACT(my_list, '$') AS list FROM help where id = " + str(id))
        l=cursor.fetchall()
        my_list=[]
        if l!=():
          l =(l[0][0])
          my_list = json.loads(l, parse_int=int) 
        loged_in_user_id = userid
        my_list = list(my_list)
        if loged_in_user_id in my_list and my_list!=[]:
            command = "You can Vote only once"
            l=score_question(0,id)
            return str(l)
        else:
            my_list.append(loged_in_user_id)
            sql3 = "DELETE FROM help WHERE id = " + str(id)
            cursor.execute(sql3)
            conn.commit()
            sql2 = "INSERT into help  (id, my_list) VALUES (%s, %s)"
            cursor.execute(sql2,(id,json.dumps(my_list),))
            conn.commit()
            cursor.close()
            l=score_question(up,id)
            return str(l)

def check_score_count_answer(id,userid,up):
        conn = requestConnection()
        cursor = requestCursor(conn)
        l = cursor.execute("SELECT JSON_EXTRACT(my_list, '$') AS list FROM help where id = " + str(id))
        l=cursor.fetchall()
        my_list=[]
        if l!=():
          l =(l[0][0])
          my_list = json.loads(l, parse_int=int) 
        loged_in_user_id = userid
        my_list = list(my_list)
        if loged_in_user_id in my_list and my_list!=[]:
            command = "You can Vote only once"
            return str(one_ans(0,id))
        else:
            my_list.append(loged_in_user_id)
            sql3 = "DELETE FROM help WHERE id = " + str(id)
            cursor.execute(sql3)
            conn.commit()
            sql2 = "INSERT into help  (id, my_list) VALUES (%s, %s)"
            cursor.execute(sql2,(id,json.dumps(my_list),))
            conn.commit()
            cursor.close()
            return str(one_ans(up,id))


def ask_question(title,content,tag,tag_list):
    conn = requestConnection()
    cursor = requestCursor(conn)
    cursor.execute('INSERT INTO Question (Title, Body,Owner_User_Id,Score) VALUES ("%s","%s", "%s","%s")',(title, content,session['id'],0))
    conn.commit()
    for k in tag_list:
            cursor.execute('INSERT INTO Tag (ID,tags) VALUES ("%s", "%s")',(total,k))
            conn.commit()
    cursor.close()
    conn.close()