from django.shortcuts import render
import sqlite3
from django.http import HttpResponse
import psycopg2
import sys
import pprint



def home(request):
    device = request.META

    conn_string = "host='ec2-107-22-167-179.compute-1.amazonaws.com' dbname='decjkd37coqf12' user='yfzfluxnsnhmrc' password='b57511fa3f7b247bf18c74a0c7fb36d9eb688bafbe4ccb37c401e1143f3d6032'"

    # print the connection string we will use to connect
    print("Connecting to database\n	->%s" % (conn_string))

    # get a connection, if a connect cannot be made an exception will be raised here
    print('before')
    conn = psycopg2.connect(conn_string)
    print('after')
    # conn.cursor will return a cursor object, you can use this cursor to perform queries
    cursor = conn.cursor()
    print(cursor)
    print('after_cursor')
    '''
    cursor.execute("""CREATE TABLE temps (
        ville           varchar(80),
        t_basse         int,           -- température basse
        t_haute         int,           -- température haute
        prcp            real,          -- précipitation
        date            date
    );""")
    '''
    print('after_execute create')

    cursor.execute("""INSERT INTO temps VALUES ('San Francisco', 46, 50, 0.25, '1994-11-27');""")
    cursor.execute("""INSERT INTO temps VALUES ('San Francisco2', 46, 50, 0.25, '1994-11-27');""")

    cursor.execute("""SELECT * FROM temps;""")
    res = cursor.fetchall()
    cursor.close()
    # commit the changes
    conn.commit()


    return HttpResponse(res)