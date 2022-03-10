#import library

#Library to manipulate string, number,datetime,...
import imp
from mimetypes import MimeTypes
import smtplib
from turtle import up
from django.dispatch import receiver
from matplotlib import image
import pandas as pd # -> To manipulate data as dataframe
import numpy as np
import streamlit as st # -> To deploy app
import datetime as dt
from PIL import Image 

#Library to send mail

import email
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#Library to call Google API
from google.oauth2 import service_account
import gspread #-> Để update data lên Google Spreadsheet
from gspread_dataframe import set_with_dataframe #-> Để update data lên Google Spreadsheet


#Library to created QR code
import barcode
from barcode.writer import ImageWriter


#Create function

#Send mail
def send_mail(text,imgage,sender_email,reciever,subject,sender_password):
    sender_email = st.secrets['SENDER_EMAIL']
    password = st.secrets['PWD_EMAIL']
    email=MIMEMultipart()
    email['From']= sender_email
    email['Subject']=subject

    #Create content as html
    part1=MIMEText(text,'html')
    email.attach(part1)

    # Create content as image
    # fp=Image.open(imgage)
    # # img=MIMEImage(fp)
    # email.attach(fp)

    #Create content as attach file
    # with Image.open(imgage) as f:
    #     file_data = f
    #     # file_name = f.name
    #     email.attach(file_data, maintype='application', subtype = 'octet-stream', filename='file_name')

    #Send mail

    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_email, password) #login with mail_id and password

    email['To'] = reciever
    text = email.as_string()
    session.sendmail(sender_email, reciever, text)

#Created QR code base on input
def bar_code(qr_code_t):
    ean=barcode.get('code128',qr_code_t,writer=ImageWriter())
    filename=ean.save('code128',{'module_width':0.15,"module_height":6, "font_size":11, "text_distance": 1, "quiet_zone": 1})
    return filename


#upload mutiple file on streamlit and read them
def read_file(df):
    type_file=df.name.split('.')[1]
    if type_file.upper()=='CSV':
        data=pd.read_csv(df)
    elif type_file.upper()=='XLSX':
        data=pd.read_excel(df)
    else:
        st.warning('please upload correct csv/excel files to continute')
    return data
def up_load():
    list_file=st.file_uploader('upload file',accept_multiple_files=True)
    for index,file in enumerate(list_file,start=1):
        index=read_file(file)
        index

#call data from Google sheet by API
def pull_data(file_name,sheet_name):
    #Library to call Google API
    from google.oauth2 import service_account
    import gspread #-> Để update data lên Google Spreadsheet
    from gspread_dataframe import set_with_dataframe #-> Để update data lên Google Spreadsheet 
    #Call Credetials
    credentials=service_account.Credentials.from_service_account_info(
        st.secrets['gcp_service_account'],
        scopes=['https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'],)

    gc=gspread.authorize(credentials)
    sh=gc.open(file_name).worksheet(sheet_name)
    sheet=sh.get_all_records()
    df=pd.DataFrame(sheet).astype(str)
    df
file='Kho NVL - NCC'
sheet='Sheet1'
# pull_data(file,sheet)


