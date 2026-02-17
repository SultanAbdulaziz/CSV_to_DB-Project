import pandas as pd
import streamlit as st
import src.pipeline as pipe


st.set_page_config(
    page_title = "SQLify",
    page_icon = ":star:",
    layout = "wide",
    menu_items={
        'About': 'This is deveolped using pandas and streamlit by Sultan 2026'
    }
)
st.title("SQLify")
st.subheader("CSV to mySQL parser")
st.divider()

uploaded_files = st.sidebar.file_uploader("Upload CSV Files here.",accept_multiple_files=True,type="csv")

limit: int = (st.sidebar.number_input("Rows Limit",value = 1000,format="%d"))

sql_type = st.sidebar.selectbox("DBMS",("mySQL","PostgreSQL","SQLite"),index = None,placeholder = "mySQL")

@st.cache_data
def start(df,sql_type):
    result_list = pipe.initialize_columns(df,sql_type)
    return result_list


if uploaded_files and sql_type is not None:
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_csv(uploaded_file)   
            result_set = start(df,sql_type)
            column_Names = list(result_set[0])
            column_dTypes = list(result_set[1])
            column_constraints = list(result_set[2])
            st.sidebar.header(":blue[_Table_] Name",divider = "red")
            table_Name = st.sidebar.text_input("Table Name",str(uploaded_file.name).split(sep = '.')[0])
            st.sidebar.header(":blue[_Column_] Names",divider = "red")
            pkColumn = st.sidebar.selectbox("Select pk Column",column_Names,index = 0)
            pkindex = column_Names.index(pkColumn)
            for i in range(len(column_Names)):
                column_Names[i] = st.sidebar.text_input(f"{i}. Column Name",value=column_Names[i],key=f"colname_{hash(uploaded_file.name)}_{i}")
            sql = pipe.SQL_Builder(table_Name,column_Names,column_dTypes,column_constraints,df,limit,pkindex)
            st.header(f"{str(uploaded_file.name).split(".")[0]} :blue[_SQL_] Code",divider = "red")
            if "NOT NULL" not in str(column_constraints[pkindex]): st.header(":red[*Warning*] PK could be NULL.")
            elif "UNIQUE" not in str(column_constraints[pkindex]): st.header(":red[*Warning*] PK is not UNIQUE.")
            st.code(sql,language = "plsql")
        except Exception as e:
            st.write(f":red[_ERROR_] {e}")



elif uploaded_files: st.header("Select DBMS")
elif sql_type is not None: st.header("Upload Files through the sidebar.")
else: st.header("Upload Files through the sidebar and Select DBMS.")

