import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import tempfile
import os
import src.pipeline as pipe

st.set_page_config(
    page_title = "CSV to mySQL parser",
    page_icon = ":star:",
    layout = "wide",
    menu_items={
        'About': 'This is deveolped using pandas and streamlit by Sultan 2026'
    }
)
st.title("Streamlit CSV to mySQL generator 🚀")

uploaded_files = st.file_uploader(
    "Upload CSV Files here.",accept_multiple_files=True,type="csv"
)

if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        st.header(":blue[_SQL_] Code",divider = "red")
        df = pd.read_csv(uploaded_file)
        sql = pipe.tomySQL(df,str(uploaded_file.name).split(sep = '.')[0],1000)
        st.code(sql,language = "SQL")

else:
    st.header("No File Uploaded")




