import pandas as pd 
from pathlib import Path
#import argparse

def initialize_columns(df: pd.DataFrame,sql_type: str):
    
    def data_type_convertor(s: str,sql_type: str):
        TYPE_MAP = {
           "mySQL":       ["INT","FLOAT","VARCHAR(250)"],
            "PostgreSQL":  ["INT","REAL","VARCHAR(250)"],
            "SQLite":      ["INTEGER","REAL","TEXT"]
        }
        if s == "int64": i=0
        elif s == "float64":i=1
        else: i=2
        return TYPE_MAP[sql_type][i]

    def column_constraints_evaluater(series: pd.Series):
        if not series.isna().sum() > 0: return "NOT NULL"
        elif series.dropna().nunique() == series.dropna().count(): return "UNIQUE"
        else: return ""
    
    column_Names = (df.keys())
    column_dTypes = []
    column_constraints = []

    for column in column_Names:
        column_dTypes.append(data_type_convertor(str(df[column].dtype),sql_type))
        column_constraints.append(column_constraints_evaluater(df[column]))
    
    return [column_Names,column_dTypes,column_constraints]

def SQL_Builder(table_Name: str,column_Names: list,column_dTypes: list,column_constraints: list,df: pd.DataFrame,limit: int):
    df.columns = column_Names
    SQL = []
    SQL.append("CREATE TABLE "+table_Name+" (\n")
    
    SQL.append(column_Names[0]+" "+column_dTypes[0]+" PRIMARY KEY "+column_constraints[0]+",\n") #First Column is PRIMARY KEY
    for i in range(1,len(column_Names)):
        SQL.append(column_Names[i]+" "+column_dTypes[i]+" "+column_constraints[i]+",\n")
    
    last_line = SQL.pop()
    SQL.append(last_line.rstrip(',\n') + "\n")
    SQL.append(");\n")
    return insert_statement_builder(table_Name,column_Names,column_dTypes,column_constraints,df,SQL,limit)

def insert_statement_builder(table_Name: str,column_Names: list,column_dTypes: list,column_constraints,df: pd.DataFrame,SQL: list,limit: int):
    for i in range(min(len(df),limit)):
        insert_statement = ["INSERT INTO "+table_Name+" VALUES ("]
        row_values = []
        for column in range(len(column_Names)):
            value = df.iloc[i][column_Names[column]]
            if pd.isna(value):
                row_values.append("NULL")
            else:
                if column_dTypes[column] == "VARCHAR(250)" or column_dTypes[column] == "TEXT":
                  row_values.append("\'"+str(value)+"\'")
                else :
                    row_values.append(str(value))
        insert_statement.append(",".join(row_values) + ");\n")
        SQL.append("".join(insert_statement))

    return ("".join(SQL))





"""
    with open("mySQL_output","w") as file:
        file.write("".join(SQL))
        return Path(file.name)

CLI args ->
parser = argparse.ArgumentParser(description="A script that parses CSV to and outputs mySQL query to create table and insert values.")
parser.add_argument("CSVinputFile", type=str, help="CSV File to parse")
parser.add_argument("--table_Name", type=str,default = "Null" ,help="Table name (default: filename)")
parser.add_argument("--limit", type=int, default=1000, help="Max rows to generate insert statements")


args = parser.parse_args()
table_Name = args.table_Name
if args.table_Name == "Null" : table_Name = (args.CSVinputFile.split(sep = "/")[-1]).split(sep = ".")[0]
"""