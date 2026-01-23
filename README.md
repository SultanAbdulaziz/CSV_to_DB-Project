# CSV to MySQL SQL Generator

v1.1 - Working CSV to MySQL CREATE TABLE and INSERT statements

# How to use
1. install pandas
2. run (src/pipelint yourfile.csv --table tablename --limit limit)
3. a mySQL output file will be created
   
# Features
- Pandas dtype to MySQL types (INT/VARCHAR/FLOAT) more types to be implemented
- NULL/UNIQUE detection
- First column is PRIMARY KEY
- INSERT statements for all records or limit
- CLI args

# Future improvements
error handling, multiple CSVs, MySQL executor, FastAPI UI,FORIEGN KEY detection,PRIMARY KEY selection and more
 

Sultan Abdulaziz - Jan 23, 2026


