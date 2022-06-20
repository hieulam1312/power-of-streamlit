from calendar import month
import json
from locale import currency
import secrets
import requests
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from gspread_dataframe import set_with_dataframe #-> Để update data lên Google Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials #-> Để nhập Google Spreadsheet Credentials

token = st.secrets['token'] #'
DATABASE_ID = st.secrets['id'] #

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"}

class NotionSync:
    def __init__(self):
        pass    

    def query_databases(self):
        database_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(database_url, headers=headers)

        return response.json()
    
    def get_projects_titles(self,data_json):
        return list(data_json["results"][0]["properties"].keys())
    

    def get_projects_data(self,data_json,projects):
        projects_data = {}
        for p in projects:
            if p=="Name" :
                projects_data['Nội dung chi'] = [data_json["results"][i]["properties"][p]["title"][0]['plain_text']
                                    for i in range(len(data_json["results"])) if data_json["results"][i]["properties"][p]["title"]]
            elif p=="Property" :
                projects_data['Số tiền'] = [data_json["results"][i]["properties"][p]['rich_text'][0]['plain_text']
                                    for i in range(len(data_json["results"])) if data_json["results"][i]["properties"]["Name"]["title"]]
            elif p=="Date" :
                projects_data['Ngày chi'] = [data_json["results"][i]["properties"][p]['date']['start']
                                    for i in range(len(data_json["results"])) if data_json["results"][i]["properties"]["Name"]["title"]]      
            elif p=="Tags" :
                projects_data['Phân loại'] = [data_json["results"][i]["properties"][p]['multi_select'][0]['name']
                                    for i in range(len(data_json["results"])) if data_json["results"][i]["properties"]["Name"]["title"]]   

        return pd.DataFrame.from_dict(projects_data) 
    
def push_lsx(df,ws1):
    spreadsheet_key='1JCyNuairaKmF0KL6Sj-7IegwrrGJ366TUnkUqNxBRAE'
    import gspread_dataframe as gd
    import gspread as gs
    existing1 = gd.get_as_dataframe(ws1)
    updated1 = existing1.append(df)
    gd.set_with_dataframe(ws1,updated1)
    st.success('Done')
import gspread_dataframe as gd
import gspread as gs
import datetime as dt
credentials = service_account.Credentials.from_service_account_info(
st.secrets["gcp_service_account"],
scopes=['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'],
)
gc = gspread.authorize(credentials)                               
nsync = NotionSync()
data = nsync.query_databases()

projects = nsync.get_projects_titles(data)
df=nsync.get_projects_data(data,projects)

user=st.sidebar.text_input('User')
pw=st.sidebar.text_input('Password',type='password')
if user==st.secrets['user'] and pw==st.secrets['pw']:
    
    radio=st.sidebar.radio('Selection',['Chi phí tuần','Tổng hợp tháng','So sánh','Xuất dữ liệu'])
    if radio=='Chi phí tuần':
        st.subtitle="Chi phí tuần này"
        df
    elif radio=='Tổng hợp tháng':
        st.subtitle="Tổng hợp tháng"
        df['Số tiền']=df['Số tiền'].astype(float)
        df['Tháng chi']=df['Ngày chi'].astype('datetime64').dt.month.astype(int)
        group=df.groupby(['Tháng chi','Phân loại']).agg({'Số tiền':'sum'}).reset_index()
        data=group.pivot(index=['Phân loại'],columns='Tháng chi',values='Số tiền').reset_index()
        data['Trung bình']=data.mean(axis=1)
        data
    elif radio=='Xuất dữ liệu':
        ws1 = gc.open("FIRE - journey").worksheet("Daily-cost")
        push_lsx(df,ws1)
        
