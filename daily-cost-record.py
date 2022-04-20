import datetime as dt
from re import L
from textwrap import indent
import gspread
import streamlit as st
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from datetime import datetime
import pytz
tz = pytz.timezone('asia/ho_chi_minh')
credentials=service_account.Credentials.from_service_account_info(
    st.secrets['gcp_service_account'],
    scopes=['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive'],
)
gc=gspread.authorize(credentials)

note=st.text_area('Quickly take notes',)

list_note=note.split('\n')
dict={}
for i in range(0,len(list_note)-1):
    if i%2==0:
        dict[list_note[i]]=list_note[i+1]

data=pd.DataFrame.from_dict(dict,orient='index',columns={'Cost'}).reset_index()
data['Date record']=datetime.now(tz).date().strftime("%m/%d/%Y")
data['Hour record']=datetime.now(tz).strftime("%H:%M")

sheet=gc.open('FIRE - journey').worksheet('Daily-cost')
data_list=data.values.tolist()
sheet.append_rows(data_list)