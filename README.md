# CSV to MySQL SQL Generator

v0.1 - Working CSV to MySQL CREATE TABLE and INSERT statements

# How to use
1. import pandas
2. Put CSV in raw and input the file name in pipeline.py main(str(Path(__file__).parent.parent/"raw/  YourFile.CSV  ")) call
3. run pipeline.py
4. Copy the generated SQL and exectute
   
# Features
- Pandas dtype to MySQL types (INT/VARCHAR/FLOAT) more types to be implemented
- NULL/UNIQUE detection
- First column is PRIMARY KEY
- INSERT statements for all records

# Future improvements
CLI args, error handling, multiple CSVs, MySQL executor, FastAPI UI,FORIEGN KEY detection,PRIMARY KEY selection and more
 
Sultan Abdulaziz - Jan 23, 2026


