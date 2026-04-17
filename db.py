import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sharlin@27",  
        database="expense_tracker"
    )