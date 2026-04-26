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