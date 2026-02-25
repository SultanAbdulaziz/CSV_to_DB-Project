import os
import pandas as pd
import streamlit as st
import src.pipeline as pipe
import src.DB as DB

st.set_page_config(
    page_title = "SQLify",
    page_icon = ":star:",
    layout = "wide",
    menu_items={
        'About': 'This is deveolped using pandas, sqlalchemy and streamlit by Sultan 2026'
    }
)
st.title("SQLify")
st.subheader("CSV to mySQL parser")
st.divider()

page = st.sidebar.radio("Navigation", ["Generate SQL", "SQL Query"])

uploaded_files = st.sidebar.file_uploader("Upload CSV Files here.",accept_multiple_files=True,type=["csv","xlsx"])

# Reset engine and DB when files are uploaded or changed
if "_last_uploaded_files" not in st.session_state:
    st.session_state["_last_uploaded_files"] = None

if uploaded_files != st.session_state["_last_uploaded_files"]:
    st.session_state["_last_uploaded_files"] = uploaded_files
    st.session_state.pop("sql_statements", None)
    st.cache_data.clear()
    st.cache_resource.clear()
    if os.path.exists("in_memory.db"):
        os.remove("in_memory.db")

limit: int = (st.sidebar.number_input("Rows Limit",value = 1000,format="%d"))

sql_type = st.sidebar.selectbox("DBMS",("mySQL","PostgreSQL","SQLite"),index = None,placeholder = "mySQL")

@st.cache_data
def start(df,sql_type):
    result_list = pipe.initialize_columns(df,sql_type)
    return result_list

def load_file(file):
    """Load CSV or Excel file and return DataFrame."""
    if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return pd.read_excel(file)
    else:
        return pd.read_csv(file)
# Store SQL statements in session state for execution
if "sql_statements" not in st.session_state:
    st.session_state["sql_statements"] = []

if uploaded_files and sql_type is not None and page == "Generate SQL":
    sql_statements = []
    for uploaded_file in uploaded_files:
        try:
            df = load_file(uploaded_file)   
            result_set = start(df,sql_type)
            column_Names = list(result_set[0])
            column_dTypes = list(result_set[1])
            column_constraints = list(result_set[2])
            st.sidebar.header(f":blue[_{uploaded_file.name}_]",divider = "red")
            table_Name = st.sidebar.text_input("Table Name",str(uploaded_file.name).split(sep = '.')[0].split()[0])
            pkColumn = st.sidebar.selectbox("Select pk Column",column_Names,index = 0)
            pkindex = column_Names.index(pkColumn)
            for i in range(len(column_Names)):
                column_Names[i] = st.sidebar.text_input(f"{i}. Column Name",value=column_Names[i],key=f"colname_{hash(uploaded_file.name)}_{i}")
            sql = pipe.SQL_Builder(table_Name,column_Names,column_dTypes,column_constraints,df,limit,pkindex)
            sql_statements.append(sql)
            st.header(f"{str(uploaded_file.name).split('.')[0]} :blue[_SQL_] Code",divider = "red")
            if "NOT NULL" not in str(column_constraints[pkindex]): st.header(":red[*Warning*] PK could be NULL.")
            elif "UNIQUE" not in str(column_constraints[pkindex]): st.header(":red[*Warning*] PK is not UNIQUE.")
            st.code(sql,language = "plsql")
        except Exception as e:
            st.write(f":red[_ERROR_] {e}")
    # Store generated SQL in session state
    st.session_state["sql_statements"] = sql_statements

elif uploaded_files and page == "Generate SQL": st.header("Select DBMS")
elif sql_type is not None and page == "Generate SQL": st.header("Upload Files through the sidebar.")
elif page == "Generate SQL": st.header("Upload Files through the sidebar and Select DBMS.")

@st.cache_resource
def startDB(sql_statements_tuple):
    # Execute all SQL statements to create tables and insert data
    engine = DB.initialize_db(list(sql_statements_tuple), filepath="in_memory.db")
    return engine

if page == "SQL Query":
    st.title("SQL Query Console")
    st.divider()
    sql_statements = st.session_state.get("sql_statements", [])
    if not sql_statements:
        st.warning("No SQL generated. Go to 'Generate SQL' page and upload files first.")
    else:
        # Convert list to tuple for cache_resource (lists are not hashable)
        engine = startDB(tuple(sql_statements))
        if not engine:
            st.warning("No database initialized.")
        else:
            query = st.text_area("Enter SQL query:", height=150)
            if st.button("Run Query"):
                if query:
                    try:
                        result_df = DB.run_query(engine, query)
                        st.success(f"✓ Query executed successfully • {len(result_df)} rows returned")
                        st.dataframe(result_df,width="stretch",height=500)
                    except Exception as e:
                        error_type = type(e).__name__
                        error_msg = str(e).split('\n')[0] if '\n' in str(e) else str(e)
                        
                        with st.expander("❌ Query Error", expanded=True):
                            st.error(f"**{error_type}**")
                            st.code(error_msg, language="text")
                            
                            with st.container():
                                st.caption("**Your Query:**")
                                st.code(query, language="sql")
                else:
                    st.info("Enter a query to run.")

