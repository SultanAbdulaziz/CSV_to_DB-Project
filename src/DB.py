from typing import Optional, Tuple
import sqlalchemy as sql
from sqlalchemy.engine import Engine
import pandas as pd
import src.pipeline as pipe
     
def initialize(**kwargs) -> Tuple[Engine, str]:
        filepath = kwargs.get("filepath")
        url = f"sqlite:///{filepath}" if filepath else "sqlite:///:memory:"
        engine = sql.create_engine(url)
        return engine, url


def execute_statements(engine: Engine, sql_text: str) -> None:
    """Execute one or more SQL statements against the engine."""
    statements = []
    current = []
    in_quote = False
    
    for i, char in enumerate(sql_text):
        if char == "'" and (i == 0 or sql_text[i-1] != '\\'):
            in_quote = not in_quote
        
        if char == ';' and not in_quote:
            stmt = ''.join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
        else:
            current.append(char)
    
    # Add last statement
    stmt = ''.join(current).strip()
    if stmt:
        statements.append(stmt)
    
    with engine.begin() as conn:
        for stmt in statements:
            conn.exec_driver_sql(stmt)

def run_query(engine: Engine, query: str) -> pd.DataFrame:
    return pd.read_sql_query(query, con=engine)

def initialize_db(sql_statements: list, **kwargs) -> Engine:
    """Initialize DB and execute all SQL statements (CREATE TABLE + INSERT)."""
    filepath = kwargs.get("filepath", "in_memory.db")
    engine = initialize(filepath=filepath)[0]
    # Execute all SQL statements to create tables and insert data
    for sql in sql_statements:
        execute_statements(engine, sql)
    return engine

