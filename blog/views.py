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




from django.http import HttpResponse
from django.shortcuts import redirect
import xlsxwriter
import pandas as pd
from pandas import ExcelWriter
import sqlite3
import csv
from io import BytesIO, StringIO
from django.http import StreamingHttpResponse
from xlsxwriter.workbook import Workbook
from datetime import datetime
import numpy as np
from openpyxl.writer.excel import save_virtual_workbook

def some_view(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    xlsx_data = WriteToExcel(weather_period, town)
    response.write(xlsx_data)
    return response



# In[166]:

def process_time_seconds(a):
    datetime_object = datetime.strptime(a, '%H:%M:%S.%f')
    datetime_object_ref = datetime.strptime('00:00:00.00', '%H:%M:%S.%f')
    temps_ok=(datetime_object-datetime_object_ref).total_seconds()
    return(temps_ok)


# In[75]:

def calcul_diff_temps(a,b):
    diff = a-b
    diff=float(format(diff, '.2f'))
    return diff


# In[ ]:

def process_date(date):
    return datetime.strptime(date, "%d/%m/%Y")


# In[113]:

def is_saison_en_cours(date):
    now_time = datetime.utcnow()
    diff = now_time-date
    days = diff.days
    if days<365:
        return(True)
    else :
        return False




def get_prog_race(lastname,firstname,race,working_df):
    swimmer_df = working_df.query("lastname=='"+str(lastname)+"' & firstname == '"+str(firstname)+"'")
    swimmer_df_nage = swimmer_df.query("race =='"+race+"'")
    swimmer_df_nage_saison = swimmer_df_nage.query("saison_en_cours==True")
    swimmer_df_nage_past = swimmer_df_nage.query("saison_en_cours==False")
    if len(swimmer_df_nage_saison)==0:
        return np.nan
    record_past = swimmer_df_nage_past['temps_ok'].min()
    record_saison = swimmer_df_nage_saison['temps_ok'].min()
    ratio = 1-(min(record_past,record_saison)/max(record_past,record_saison))
    sign = (record_past-record_saison)/abs((record_past-record_saison))
    prog = ratio*sign
    return prog


# In[355]:

def get_prog_swimmer(lastname,firstname,working_df):
    prog_serie = pd.Series()
    for race in working_df.query("lastname=='"+str(lastname)+"' & firstname == '"+str(firstname)+"'")['race'].unique():
        prog = get_prog_race(lastname,firstname,race,working_df)
        prog_serie.loc[race] = prog
        prog_serie = prog_serie[~pd.isnull(prog_serie)]
        prog_serie.name = lastname+' '+firstname
    if len(prog_serie)==0:
        return None
    prog_serie.loc['Moyenne'] = prog_serie.mean()
    prog_serie=prog_serie.apply(lambda x : float(format(x, '.3f')))*100
    return prog_serie


# In[387]:

def get_prog_list_names(names,working_df):
    dict_progs = {}
    for name in names:
        lastname = name.split(' ')[0]
        firstname = name.split(' ')[1]
        name_id = lastname+' '+firstname
        progressions = get_prog_swimmer(lastname,firstname,working_df)
        if str(progressions)!='None':
            dict_progs[name_id]=progressions
    return dict_progs


# In[485]:

def get_group_avg(groupe):
    total = 0
    for item in groupe.keys():
        print(item)
        total += groupe[item]['Moyenne']
    moy_groupe = total/len(groupe.keys())
    groupe['Moyenne'] = pd.Series(moy_groupe,name='Moyenne')
    print(groupe)
    return groupe

def index(request):
    print('hello')
    return redirect('process')

def save_xls(list_dfs, xls_path):
    bio = BytesIO()

    # By setting the 'engine' in the ExcelWriter constructor.
    writer = ExcelWriter(bio, engine='xlsxwriter')
    for n, df in enumerate(list_dfs):
        if df.columns[0]!='Moyenne':
            df.to_excel(writer,df.columns[0])
        else : moyenne = df
    moyenne.to_excel(writer,moyenne.columns[0])
    print(writer)



    # Save the workbook
    writer.save()

    # Seek to the beginning and read to copy the workbook to a variable in memory
    bio.seek(0)
    workbook = bio.read()
    return workbook


def process(request):
    #conn = sqlite3.connect("table2")
    #cur = conn.cursor()
    #PandasDataFrame=pd.read_sql_query("select * from rankings;", conn).set_index('index')
    PandasDataFrame=pd.read_csv('/static/rankings_natcourse_25.csv',encoding='latin-1',sep=';')
    working_df = PandasDataFrame.copy()
    #response = HttpResponse(content_type='text/csv')
    #response['Content-Disposition'] = 'attachment; filename=filename.csv'
    #PandasDataFrame.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
    working_df['temps_ok'] = PandasDataFrame['rankingtime'].apply(process_time_seconds)
    print('ok')
    print(PandasDataFrame['rankingdate'].iloc()[2])
    working_df['date_ok'] = PandasDataFrame['rankingdate'].apply(process_date)

    print('ok2')
    working_df['saison_en_cours'] = working_df['date_ok'].apply(is_saison_en_cours)
    print('ok3')
    working_df['nom+prenom'] = working_df['lastname'] + ' ' + working_df['firstname']

    year_1995 = working_df.query("birthyear == " + str(1996))

    year_1995names = list(year_1995['nom+prenom'].unique())

    groupe = get_prog_list_names(year_1995names,working_df)

    groupe_with_avg = get_group_avg(groupe)

    RANKINGS_MON = './ranking_res.xlsx'
    list_sheets = [pd.DataFrame(groupe_with_avg[k]) for k in groupe_with_avg.keys()]
    writer = save_xls(list_sheets, RANKINGS_MON)

    response = HttpResponse(writer,
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=test.xlsx"

    return response