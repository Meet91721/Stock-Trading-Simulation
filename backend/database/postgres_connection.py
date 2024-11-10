from backend.config.pg_db_config import *
import psycopg2


def get_connection():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        print("Connected to PostgreSQL successfully")
        return conn

    except Exception as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None
        
def close_connection(conn):
    conn.close()
    print("Connection to PostgreSQL is closed")

def insert_user(fname, lname, email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"INSERT INTO users (fname, lname, email, password) VALUES ('{fname}', '{lname}', '{email}', '{password}')"
        )
        # get dbid of this user
        cursor.execute(
            f"SELECT dbid FROM users WHERE email = '{email}'"
        )
        dbid = cursor.fetchone()[0]
    except Exception as error:
        print(f"Error inserting user: {error}")
        return -1
    except psycopg2.Error as error:
        print(f"Error inserting user: {error}")
        return -2
    conn.commit()
    cursor.close()
    close_connection(conn)
    return dbid

def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT dbid, password, email_verified FROM users WHERE email = '{email}'"
    )
    data = cursor.fetchone()
    if data == None:
        return None
    cursor.close()
    close_connection(conn)
    return data

def verify_email(dbid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE users SET email_verified = TRUE WHERE dbid = '{dbid}'"
    )
    conn.commit()
    cursor.close()
    close_connection(conn)
    return 0