from calendar import month
import json
from locale import currency
import secrets
import requests
import pandas as pd
import streamlit as st


token = st.secrets('token') #'
DATABASE_ID = st.secrets('id') #

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
import datetime as dt
nsync = NotionSync()
data = nsync.query_databases()

projects = nsync.get_projects_titles(data)
df=nsync.get_projects_data(data,projects)


df['Số tiền']=df['Số tiền'].astype(float)
df['Tháng chi']=df['Ngày chi'].astype('datetime64').dt.month.astype(int)
group=df.groupby(['Tháng chi','Phân loại']).agg({'Số tiền':'sum'}).reset_index()
# data=df.pivot(index=['Ngày chi','Nội dung chi'],columns='Phân loại',values='Số tiền').reset_index()

data=group.pivot(index=['Phân loại'],columns='Tháng chi',values='Số tiền').reset_index()
data['Trung bình']=data.mean(axis=1)
data
