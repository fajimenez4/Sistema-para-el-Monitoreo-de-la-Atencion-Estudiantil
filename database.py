import psycopg2
from tkinter import messagebox
import psycopg2
from psycopg2 import sql
from tkinter import messagebox

def crear_db():
    try:
        connection = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="12345",
            port="5433",
            database="postgres"  
        )
        connection.autocommit = True
        cursor = connection.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'programa'")
        existe = cursor.fetchone()
        
        if not existe:
            cursor.execute(sql.SQL("CREATE DATABASE programa"))
        
        cursor.close()
        connection.close()
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo verificar/crear la base de datos: {e}")

def conexion_db():
    try:
        connection = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="12345",
            database="programa",
            port="5433"
        )
        connection.autocommit = True
        return connection
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
        return None  
    
