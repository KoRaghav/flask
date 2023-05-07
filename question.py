
import MySQLdb

def requestConnection():
    mydb = MySQLdb.connect(host='localhost',
    user='root',
    passwd='root',
    db='askq')
    return mydb

def requestCursor(conn):
    return conn.cursor()



def questionTag_from_id(id): # list of tag from question id
    conn=requestConnection()
    cursor=requestCursor(conn)
    l=cursor.execute('SELECT tags FROM Tag where id = ' + str(id))
    l=cursor.fetchall()
    tag_list=[]
    for k in range(0,len(l)):
        tag_list.append(l[k][0])
    cursor.close()
    conn.close()
    return tag_list



def question_from_tag(tag,offset):
    Ans=[]
    conn=requestConnection()
    cursor=requestCursor(conn)
    tags = '"' + tag + '"'
    f = str(offset)
    a=cursor.execute('select ID from Tag where tags = '+ tags +' limit 3 offset '+ f  )
    a=cursor.fetchall()
    for i in range(len(a)):
        l=cursor.execute('SELECT * FROM Question where id = ' + str(a[i][0]))
        l=cursor.fetchall()
        m = cursor.execute('SELECT tags FROM Tag where id = ' + str(a[i][0]))
        m = cursor.fetchall()
        M = []
        for i in range(len(m)):
            M.append( m[i][0])
        L = list(l)
        L.append(M)
        Ans.append(L)  
    cursor.close()
    conn.close()        
    return Ans


def complete_question_with_taglist(l,n):
    ans=[]
    for i in range(0,n):
        a=l[i][0]
        b=questionTag_from_id(a)
        c=[]
        c.append(l[i])
        c.append(b)
        ans.append(c)
    return ans


def question_page(val): 
    conn=requestConnection()
    cursor=requestCursor(conn)
    p=cursor.execute('SELECT count(ID) FROM Question') 
    p=cursor.fetchall()
    total = (p[0][0])
    cursor.close()
    conn.close()
    return total



def question_page2(val,page): 
    conn=requestConnection()
    cursor=requestCursor(conn)
    per_page=3
    offset=(page-1)*per_page
    if val==0:
        l=cursor.execute('SELECT * FROM Question ORDER BY Creation_Date DESC limit 3 offset '+str(offset))
    elif val==1:
        l=cursor.execute('SELECT * FROM Question ORDER BY Score DESC limit 3 offset '+str(offset))
    l=cursor.fetchall()
    n=len(l)
    ans=complete_question_with_taglist(l,n)
    cursor.close()
    conn.close()
    return ans


def showQuestion_byscore_help(page):
    a=question_page2(1,page)
    return a

def sort_que_by_time(page):
    b=question_page2(0,page)
    return b

def sort_que_by_time_number():
    b=question_page(0)
    return b    


def pagefunction2(page,tag='flex'):
    per_page=3
    offset=(page-1)*per_page
    l=question_from_tag(tag,offset)
    return l

def pagefunction_number(tag='flex'):
    conn = requestConnection()
    cursor = requestCursor(conn)
    per_page=3
    page = 1
    offset=(page-1)*per_page
    tags='"'+tag+'"'
    p=cursor.execute('SELECT count(id) FROM Tag where tags='+str(tags))
    p=cursor.fetchall()
    total = (p[0][0])
    cursor.close()
    conn.close()
    return total


def  question_from_list_of_tag(taglist,page):
    conn = requestConnection()
    cursor = requestCursor(conn)
    idlist=[]
    offset=(page-1)*3
    for k in taglist:
       k='"'+k+'"'
       b=cursor.execute('select id from Tag where tags='+str(k))
       b=cursor.fetchall()
       idlist += [x[0] for x in b]
    ans=[]
    n=len(idlist)
    question_id_string = "("+','.join(map(str, idlist))+")"
    p=cursor.execute(f"""select * from Question where id in {question_id_string} limit 3 offset {offset}""")
    p=cursor.fetchall()
    ans.append(complete_question_with_taglist(p,len(p)))
    cursor.close()
    conn.close()
    return ans[0]

def  question_from_list_of_tag_number(taglist):
    conn = requestConnection()
    cursor = requestCursor(conn)
    idlist=[]
    for k in taglist:
       k='"'+k+'"'
       b=cursor.execute('select id from Tag where tags='+str(k))
       b=cursor.fetchall()
       idlist += [x[0] for x in b]
    ans=[]
    n=len(idlist)
    return n


def  question_from_list_of_tag_ml(tags,page):
    conn = requestConnection()
    cursor = requestCursor(conn)
    offset=(page-1)*3
    if not tags: return "false"
    question_id_string = ' + '.join([f"""MATCH (title,Body) against ('"{x}"' in BOOLEAN MODE) * {int(y*10000)} """ for (x,y) in tags])
    query = f"""select * , {question_id_string} AS score from Question ORDER BY score DESC limit 3 offset {offset}"""
    p=cursor.execute(query)
    p=cursor.fetchall()
    ans=[]
    ans.append(complete_question_with_taglist(p,len(p)))
    cursor.close()
    conn.close()
    return ans[0]


# we are getting a list and thus sort them by score 
def sort_quesbyTag(tag,page): 
    offset=(page-1)*3
    ans=question_from_tag(tag,offset)
    return ans

