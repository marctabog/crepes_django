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
from .forms import ContactForm
from django.shortcuts import render

def some_view(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report.xlsx'
    xlsx_data = WriteToExcel(weather_period, town)
    response.write(xlsx_data)
    return response

def process_name(x):
    x=x.replace("'","_")
    return(x)


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
        print('name')
        print(name)
        lastname = name.split(' ')[0]
        firstname = name.split(' ')[1]
        name_id = lastname+' '+firstname

        progressions = get_prog_swimmer(lastname,firstname,working_df)

        if str(progressions)!='None':  
            dict_progs[name_id]=progressions
    return dict_progs


# In[485]:

def get_group_avg(groupe):
    print('GROUPE')
    print(groupe)
    total = 0
    for item in groupe.keys():
        total += groupe[item]['Moyenne']
    moy_groupe = total/len(groupe.keys())
    groupe['Moyenne'] = pd.Series(moy_groupe,name='Moyenne')
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
    #print(writer)



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
    PandasDataFrame=pd.read_csv('rankings_natcourse_25.csv',encoding='latin-1',sep=';')
    working_df = PandasDataFrame.copy()
    #response = HttpResponse(content_type='text/csv')
    #response['Content-Disposition'] = 'attachment; filename=filename.csv'
    #PandasDataFrame.to_csv(path_or_buf=response,sep=';',float_format='%.2f',index=False,decimal=",")
    working_df['temps_ok'] = PandasDataFrame['rankingtime'].apply(process_time_seconds)
    #print('ok')
    #print(PandasDataFrame['rankingdate'].iloc()[2])
    working_df['date_ok'] = PandasDataFrame['rankingdate'].apply(process_date)

    #print('ok2')
    working_df['saison_en_cours'] = working_df['date_ok'].apply(is_saison_en_cours)
    #print('ok3')
    working_df['nom+prenom'] = working_df['lastname'] + ' ' + working_df['firstname']


    groupe = get_prog_list_names(year_1995names,working_df)
    groupe_with_avg = get_group_avg(groupe)

    RANKINGS_MON = './ranking_res.xlsx'
    list_sheets = [pd.DataFrame(groupe_with_avg[k]) for k in groupe_with_avg.keys()]
    writer = save_xls(list_sheets, RANKINGS_MON)

    response = HttpResponse(writer,
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=test.xlsx"

    return response


def contact(request):
    PandasDataFrame = pd.read_csv('rankings_natcourse_25.csv', encoding='latin-1', sep=';')
    working_df = PandasDataFrame.copy()
    working_df['firstname'] = working_df['firstname'].apply(process_name)
    working_df['lastname'] = working_df['lastname'].apply(process_name)
    working_df['temps_ok'] = PandasDataFrame['rankingtime'].apply(process_time_seconds)
    working_df['date_ok'] = PandasDataFrame['rankingdate'].apply(process_date)
    working_df['saison_en_cours'] = working_df['date_ok'].apply(is_saison_en_cours)
    working_df['nom+prenom'] = working_df['lastname'] + ' ' + working_df['firstname']

    # Construire le formulaire, soit avec les données postées,
    # soit vide si l'utilisateur accède pour la première fois
    # à la page.
    form = ContactForm(request.POST or None)
    # Nous vérifions que les données envoyées sont valides
    # Cette méthode renvoie False s'il n'y a pas de données
    # dans le formulaire ou qu'il contient des erreurs.
    if form.is_valid():
        # Ici nous pouvons traiter les données du formulaire
        year_group = form.cleaned_data['annee_naissance_groupe']
        names_bool = form.cleaned_data['choix_liste_noms']
        list_group = form.cleaned_data['liste_nageurs']
        group_name = form.cleaned_data['nom_du_groupe']

        if names_bool:
            name_list=list_group.split('/')
        else :
            group_by_year = working_df.query("birthyear == " + str(year_group))
            name_list = list(group_by_year['nom+prenom'].unique())
        print('before')
        groupe_tmp = get_prog_list_names(name_list, working_df)
        print('len(dict_progs)')
        print(len(groupe_tmp))
        if len(groupe_tmp)==0:
                    print('oki')
                    text = "Erreur, aucune course cette saison pour les nageurs entrés!"
                    return HttpResponse(text)
        
        groupe_with_avg = get_group_avg(groupe_tmp)
        
        # year_1995 = working_df.query("birthyear == " + str(1996))

        # year_1995names = list(year_1995['nom+prenom'].unique())
        #year_1995names_0 = working_df.loc[
        #working_df['nom+prenom'].isin(['TABOGA Vincent', 'TABOGA Marc', 'COUDERT Rémi'])]
        #year_1995names = list(year_1995names_0['nom+prenom'].unique())
        #print(year_1995names)

        # Nous pourrions ici envoyer l'e-mail grâce aux données
        # que nous venons de récupérer
        RANKINGS_MON = './'+group_name+'.xlsx'
        list_sheets = [pd.DataFrame(groupe_with_avg[k]) for k in groupe_with_avg.keys()]
        writer = save_xls(list_sheets, RANKINGS_MON)

        response = HttpResponse(writer,
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename="+group_name+".xlsx"
        
        return response
    print('here')
    # Quoiqu'il arrive, on affiche la page du formulaire.
    return render(request, 'contact.html', locals())
