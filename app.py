import streamlit as st
import mysql.connector
from PyPDF2 import PdfReader
from openai import OpenAI

client= OpenAI(api_key="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

def db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",        
        database="notes_db"
    )

st.title("Ai Notes generator")

menu =  st.sidebar.selectbox("Menu",["Login","Register"])

if menu == "Register":
    u=st.text_input("Username",key="reg_user")
    p=st.text_input("Password",key="reg_pass",type="password")
    if st.button("Register"):
        d=db();c=d.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users(username VARCHAR(50) , password VARCHAR(50))")
        c.execute("INSERT INTO users VALUES(%s,%s)",(u,p))
        d.commit()
        st.success("Registered")
        