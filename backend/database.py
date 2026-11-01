import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="monitoria_db",
        user="postgres",
        password="admin123" # Altere caso tenha definido outra palavra-passe
    )
    return conn