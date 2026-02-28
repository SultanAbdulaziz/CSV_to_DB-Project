# Import necessary libraries
import os
import pandas as pd
import streamlit as st
import src.pipeline as pipe
import src.DB as DB

# Configure the Streamlit page settings
st.set_page_config(
    page_title = "SQLify",
    page_icon = "SQLify_Logo.png",
    layout = "wide",
    menu_items={
        'About': 'This is deveolped using pandas, sqlalchemy and streamlit by Sultan 2026'
    }
)

# Display logo and page title
st.logo("SQLify_Logo.png",size="large")
st.title("SQLify")
st.subheader("CSV to mySQL parser")
st.divider()

# Sidebar navigation to switch between pages
page = st.sidebar.radio("Navigation", ["Generate SQL", "SQL Query"])

# File uploader for CSV/Excel files
uploaded_files = st.sidebar.file_uploader("Upload CSV Files here.",accept_multiple_files=True,type=["csv","xlsx"])

# Track uploaded files to detect changes
if "_last_uploaded_files" not in st.session_state:
    st.session_state["_last_uploaded_files"] = None

# When files change, reset all cached data and database
if uploaded_files != st.session_state["_last_uploaded_files"]:
    st.session_state["_last_uploaded_files"] = uploaded_files
    st.session_state.pop("sql_statements", None)  # Clear old SQL statements
    st.session_state['disable_SQLquerypage'] = False  # Re-enable query page
    st.cache_data.clear()  # Clear Streamlit data cache
    st.cache_resource.clear()  # Clear Streamlit resource cache
    if os.path.exists("in_memory.db"):
        os.remove("in_memory.db")  # Delete old database file

# Sidebar input for row limit
limit: int = (st.sidebar.number_input("Rows Limit",value = 1000,format="%d"))

# Sidebar dropdown to select database type
sql_type = st.sidebar.selectbox("DBMS",("mySQL","PostgreSQL","SQLite"),index = None,placeholder = "mySQL")

# Cache the column analysis to avoid reprocessing on every interaction
@st.cache_data
def start(df,sql_type):
    """Analyze DataFrame and return column names, data types, and constraints."""
    result_list = pipe.initialize_columns(df,sql_type)
    return result_list

def load_file(file):
    """Load CSV or Excel file and return DataFrame."""
    if file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return pd.read_excel(file)
    else:
        return pd.read_csv(file)

# Initialize session state to store generated SQL statements
if "sql_statements" not in st.session_state:
    st.session_state["sql_statements"] = []

# Initialize flag to disable query page when PK constraints are invalid
if "disable_SQLquerypage" not in st.session_state:
    st.session_state['disable_SQLquerypage'] = False

# Store user's edited column names per file (persists across page navigation)
if "edited_columns" not in st.session_state:
    st.session_state["edited_columns"] = {}

# Store user's custom table names per file (persists across page navigation)
if "table_names" not in st.session_state:
    st.session_state["table_names"] = {}

# Store user's primary key selections per file (persists across page navigation)
if "pk_selections" not in st.session_state:
    st.session_state["pk_selections"] = {}
if uploaded_files and sql_type is not None and page == "Generate SQL":
    sql_statements = []
    has_violations = False
    for uploaded_file in uploaded_files:
        try:
            df = load_file(uploaded_file)   
            result_set = start(df,sql_type)
            column_Names = list(result_set[0])
            column_dTypes = list(result_set[1])
            column_constraints = list(result_set[2])
            
            # Restore edited column names from session state if available
            file_key = uploaded_file.name
            if file_key in st.session_state["edited_columns"]:
                column_Names = st.session_state["edited_columns"][file_key].copy()
            
            expander = st.expander(f"{uploaded_file.name}", expanded=True)
            expander.header(f":blue[_{uploaded_file.name}_]",divider = "red")

            header_cols = expander.columns(2)
            
            # Get default table name
            default_table_name = st.session_state["table_names"].get(file_key, str(uploaded_file.name).split(sep='.')[0].split()[0])
            table_Name = header_cols[0].text_input("Table Name", default_table_name, key=f"table_{hash(uploaded_file.name)}")
            st.session_state["table_names"][file_key] = table_Name
            
            # Get default pk index
            default_pk_index = st.session_state["pk_selections"].get(file_key, 0)
            pkColumn = header_cols[1].selectbox("Select pk Column", column_Names, index=default_pk_index, key=f"pk_{hash(uploaded_file.name)}")
            pkindex = column_Names.index(pkColumn)
            st.session_state["pk_selections"][file_key] = pkindex

            expander.subheader("Column Names")
            col_layout = expander.columns(3)
            for i in range(len(column_Names)):
                target_col = col_layout[i % 3]
                column_Names[i] = target_col.text_input(f"{i}. Column Name",value=column_Names[i],key=f"colname_{hash(uploaded_file.name)}_{i}")
            
            # Save edited column names to session state
            st.session_state["edited_columns"][file_key] = column_Names.copy()
            
            sql = pipe.SQL_Builder(table_Name,column_Names,column_dTypes,column_constraints,df,limit,pkindex)
            sql_statements.append(sql)
            expander.header(f"{str(uploaded_file.name).split('.')[0]} :blue[_SQL_] Code",divider = "red")
            if "NOT NULL" not in str(column_constraints[pkindex]):
                expander.header(":red[*Warning*] PK could be NULL.")
                has_violations = True
            elif "UNIQUE" not in str(column_constraints[pkindex]):
                expander.header(":red[*Warning*] PK is not UNIQUE.")
                has_violations = True
            expander.code(sql,language = "plsql")
        except Exception as e:
            expander.write(f":red[_ERROR_] {e}")
    
    st.session_state['disable_SQLquerypage'] = has_violations
    
    # Store generated SQL in session state
    st.session_state["sql_statements"] = sql_statements

elif uploaded_files and page == "Generate SQL": st.header("Select DBMS")
elif sql_type is not None and page == "Generate SQL": st.header("Upload Files through the sidebar.")
elif page == "Generate SQL": st.header("Upload Files through the sidebar and Select DBMS.")

def startDB(sql_statements):
    # Delete existing database file to start fresh
    if os.path.exists("in_memory.db"):
        os.remove("in_memory.db")
    # Execute all SQL statements to create tables and insert data
    engine = DB.initialize_db(sql_statements, filepath="in_memory.db")
    return engine

if page == "SQL Query":
    if st.session_state.get('disable_SQLquerypage'):
        st.warning("SQL Query page is disabled due to invalid primary key constraints.")
        st.stop()
    st.title("SQL Query Console")
    st.divider()
    sql_statements = st.session_state.get("sql_statements", [])
    if not sql_statements:
        st.warning("No SQL generated. Go to 'Generate SQL' page and upload files first.")
    else:
        # Initialize database fresh on every page load
        engine = startDB(sql_statements)
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
                        
                        with st.expander("Query Error", expanded=True):
                            st.error(f"**{error_type}**")
                            st.code(error_msg, language="text")
                            
                            with st.container():
                                st.caption("**Your Query:**")
                                st.code(query, language="sql")
                else:
                    st.info("Enter a query to run.")