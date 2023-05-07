import MySQLdb
from collections import defaultdict
def requestConnection():
    mydb = MySQLdb.connect(host='localhost',
    user='root',
    passwd='root',
    db='askq')
    return mydb

def requestCursor(conn):
    return conn.cursor()

def get_tags(offset=0,per_page=6):
    conn = requestConnection()
    cursor = requestCursor(conn)
    l = cursor.execute('select count(tags),tags from Tag group by tags order by count(*) desc limit 6 offset '+str(offset))
    l = list(cursor.fetchall())
    cursor.execute('SELECT count( DISTINCT(tags) ) FROM Tag')
    n=cursor.fetchall()[0][0]
    if (l==[]) or (l is None): abort(404)
    return l,n

def get_tags_list():
    conn = requestConnection()
    cursor = requestCursor(conn)
    l = cursor.execute('select tags from Tag group by tags')
    print(l)
    l = list(cursor.fetchall())
    
    if (l==[]) or (l is None): abort(404)
    return l 
